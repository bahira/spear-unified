"""Matched, opt-in small-MLP serving experiment on real handwritten digits.

Exact trained 64→128 GELU→10 weights across SpearVM, NumPy+SciPy, PyTorch
and ONNX Runtime. CPU-only; no implicit backend switch or performance claim.
The public sklearn digits dataset is real, but this is not a customer workload.

Run (after explicit optional installation):
  python -m scripts.bench_digits_mlp
  python -m scripts.bench_digits_mlp --smoke
"""
import argparse
import hashlib
import json
import math
import os
import platform
import resource
import statistics
import tempfile
import time
from pathlib import Path

from spear.spearvm import SpearVMPackedMLP, cpu_supported


SEED = 2026
THREADS = 2
REPEATS = 31
WARMUPS = 5
LOGIT_ABS_TOLERANCE = 0.005
MIN_PREDICTION_AGREEMENT = 0.99


def p95(values):
    ordered = sorted(values)
    return ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)]


def prepare_model(np, torch, load_digits, train_test_split):
    raw = load_digits()
    images = (raw.data / 16.0).astype(np.float32)
    labels = raw.target.astype(np.int64)
    x_train, x_test, y_train, y_test = train_test_split(
        images, labels, test_size=0.2, random_state=SEED, stratify=labels)
    torch.manual_seed(SEED)
    torch.set_num_threads(THREADS)
    network = torch.nn.Sequential(
        torch.nn.Linear(64, 128),
        torch.nn.GELU(approximate='none'),
        torch.nn.Linear(128, 10))
    optimizer = torch.optim.Adam(network.parameters(), lr=0.012)
    x_t = torch.from_numpy(x_train)
    y_t = torch.from_numpy(y_train)
    start = time.perf_counter()
    network.train()
    for _ in range(85):
        optimizer.zero_grad(set_to_none=True)
        logits = network(x_t)
        loss = torch.nn.functional.cross_entropy(logits, y_t)
        loss.backward()
        optimizer.step()
    training_seconds = time.perf_counter() - start
    network.eval()
    with torch.inference_mode():
        prediction = network(torch.from_numpy(x_test)).argmax(1).cpu().numpy()
    test_accuracy = float((prediction == y_test).mean())
    if test_accuracy < 0.90:
        raise ValueError('Training quality below predeclared 90% test accuracy')
    layers = []
    for index in (0, 2):
        layer = network[index]
        w = layer.weight.detach().cpu().numpy().astype(np.float32, copy=True)
        b = layer.bias.detach().cpu().numpy().astype(np.float32, copy=True)
        layers.append((w, b))
    return network, tuple(layers), x_test, y_test, {
        'data_source': 'sklearn.datasets.load_digits',
        'total_samples': int(len(images)), 'train_samples': int(len(x_train)),
        'unique_test_samples': int(len(x_test)), 'train_epochs': 85,
        'train_seconds': training_seconds, 'test_accuracy_torch': test_accuracy,
        'train_test_seed': SEED, 'stratified_holdout': True}


def build_onnx_session(network, torch, ort, path):
    options = ort.SessionOptions()
    options.intra_op_num_threads = THREADS
    options.inter_op_num_threads = 1
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    torch.onnx.export(
        network, torch.zeros(1, 64, dtype=torch.float32),
        str(path), input_names=['input'], output_names=['logits'],
        dynamic_axes={'input': {0: 'batch'}, 'logits': {0: 'batch'}},
        opset_version=17, dynamo=False)
    return ort.InferenceSession(str(path), sess_options=options,
                                providers=['CPUExecutionProvider'])


def compare_outputs(outputs, baseline, np, labels=None):
    """Never compare only runtime; enforce same results and predicted labels."""
    errors = {}
    for name, result in outputs.items():
        if (result.shape != baseline.shape or result.dtype != np.float32 or
                not np.isfinite(result).all()):
            raise ValueError(f'Invalid output shape/dtype/finite: {name}')
        err = float(np.max(np.abs(result.astype(np.float64) - baseline.astype(np.float64))))
        agreement = float(np.mean(np.argmax(result, axis=1) ==
                                  np.argmax(baseline, axis=1)))
        if err > LOGIT_ABS_TOLERANCE or agreement < MIN_PREDICTION_AGREEMENT:
            raise ValueError(f'Numerical/model quality budget exceeded: {name} '
                             f'error={err} agreement={agreement}')
        row = {'max_abs_logit_error_vs_torch': err,
               'prediction_agreement_vs_torch': agreement}
        if labels is not None:
            row['test_accuracy'] = float(np.mean(np.argmax(result, axis=1) == labels))
        errors[name] = row
    return errors


def timed_batches(inputs, runners, repeats):
    # Balanced rotations and reversals avoid one method always being timed
    # first. Timed contract: prepared float32 NumPy array -> output ndarray.
    for runner in runners.values():
        for _ in range(WARMUPS):
            runner(inputs)
    raw = {name: [] for name in runners}
    sink = 0.0
    names = list(runners)
    for rep in range(repeats):
        sequence = names[rep % len(names):] + names[:rep % len(names)]
        if rep % 2:
            sequence.reverse()
        for name in sequence:
            start = time.perf_counter_ns()
            output = runners[name](inputs)
            raw[name].append(time.perf_counter_ns() - start)
            sink += float(output[0, 0])
    return {
        'median_ns_per_batch': {k: int(statistics.median(v)) for k, v in raw.items()},
        'p95_ns_per_batch': {k: p95(v) for k, v in raw.items()},
        'raw_ns_per_batch': raw, 'sink': sink}


def run(smoke=False):
    if not cpu_supported():
        return {'status': 'unsupported', 'reason': 'Linux x86_64 AVX2+FMA required'}
    import numpy as np
    import torch
    import onnxruntime as ort
    import scipy.special as special
    import spur_math as sm
    from sklearn.datasets import load_digits
    from sklearn.model_selection import train_test_split

    os.environ.setdefault('OMP_NUM_THREADS', str(THREADS))
    os.environ.setdefault('OPENBLAS_NUM_THREADS', str(THREADS))
    network, layers, test_data, labels, data_info = prepare_model(
        np, torch, load_digits, train_test_split)
    weight_hash = hashlib.sha256(b''.join(
        item.tobytes() for pair in layers for item in pair)).hexdigest()
    start = time.perf_counter()
    packed = SpearVMPackedMLP(layers)
    packed_setup_ms = (time.perf_counter() - start) * 1000.0
    (w1, b1), (w2, b2) = layers

    with tempfile.TemporaryDirectory(prefix='spear-onnx-') as folder:
        start = time.perf_counter()
        session = build_onnx_session(network, torch, ort, Path(folder) / 'digits.onnx')
        onnx_setup_ms = (time.perf_counter() - start) * 1000.0

        def packed_runner(x):
            return packed.compute(x)['values']

        def unpacked_runner(x):
            return sm.matmul_nt(sm.matmul_nt_gelu(x, w1, b1), w2) + b2

        def numpy_scipy_runner(x):
            h = x @ w1.T + b1
            h = h * special.ndtr(h)
            return np.asarray(h @ w2.T + b2, dtype=np.float32)

        def torch_runner(x):
            with torch.inference_mode():
                return network(torch.from_numpy(x)).detach().cpu().numpy()

        def onnx_runner(x):
            return session.run(['logits'], {'input': x})[0]

        runners = {'spearvm_packed': packed_runner,
                   'spearvm_unpacked': unpacked_runner,
                   'numpy_scipy': numpy_scipy_runner,
                   'pytorch_cpu': torch_runner,
                   'onnxruntime_cpu': onnx_runner}
        sizes = (1, 32) if smoke else (1, 32, 256, 360, 1024)
        results = []
        for count in sizes:
            # For batch > 360, test inputs are repeated explicitly; do not
            # present those as 1024 independent digits or model-quality data.
            x = np.ascontiguousarray(
                np.tile(test_data, (math.ceil(count / len(test_data)), 1))[:count],
                dtype=np.float32)
            output = {label: runner(x) for label, runner in runners.items()}
            accuracy = compare_outputs(
                output, output['pytorch_cpu'], np,
                labels=labels if count == len(test_data) else None)
            timing = timed_batches(x, runners, 5 if smoke else REPEATS)
            medians = timing['median_ns_per_batch']
            strongest = min((name for name in medians if name != 'spearvm_packed'),
                            key=lambda name: medians[name])
            results.append({
                'batch': count, 'unique_input_rows': min(count, len(test_data)),
                'rows_repeated': count > len(test_data),
                'quality': accuracy,
                'strongest_non_packed_baseline': strongest,
                'packed_vs_strongest_baseline_duration_ratio':
                    medians['spearvm_packed'] / medians[strongest],
                **timing,
            })

    report = {
        'status': 'ok', 'experiment': 'trained_digits_64_128_10',
        'backend_promoted': False,
        'source': 'sklearn digits real handwritten images; benchmark synthetic repeated serving calls',
        'seed': SEED, 'weights_sha256': weight_hash,
        'platform': platform.platform(), 'python': platform.python_version(),
        'numpy_version': np.__version__, 'pytorch_version': torch.__version__,
        'onnxruntime_version': ort.__version__, 'threads': THREADS,
        'data': data_info,
        'packed_setup_ms': packed_setup_ms, 'onnx_export_session_setup_ms': onnx_setup_ms,
        'repeats': 5 if smoke else REPEATS, 'warmups': WARMUPS,
        'logit_abs_budget': LOGIT_ABS_TOLERANCE,
        'prediction_agreement_minimum': MIN_PREDICTION_AGREEMENT,
        'timed_contract': 'preallocated contiguous f32 ndarray -> f32 output ndarray; no images-to-features or network IO',
        'excluded': 'dataset loading, model training, weight packing, ONNX export/session, JSON serialization/network',
        'peak_process_rss_kb': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'limitations': 'Shared CI host CPU scheduling/noise; model is a tiny research demo, '
                       'not a customer workload. Training and serving shape decisions '
                       'not matched to a commercial deployment; no promotion.',
        'results': results,
    }
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke', action='store_true')
    args = parser.parse_args()
    report = run(smoke=args.smoke)
    print(json.dumps(report, indent=2, allow_nan=False))
    return 0 if report['status'] in ('ok', 'unsupported') else 2


if __name__ == '__main__':
    raise SystemExit(main())

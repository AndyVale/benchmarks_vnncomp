import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gen_instances as generator
from cli_gen_instances import main as cli_main
from GUI_gen_instance.logic import logic as GuiLogic


def metadata_frame():
    return pd.DataFrame([
        {"architecture": "convolutional", "benchmark": "demo", "onnx": "a.onnx", "node_types": ["Relu", "Conv"], "n_params": 10},
        {"architecture": "fullyconnected", "benchmark": "other", "onnx": "b.onnx", "node_types": ["Gemm"], "n_params": 100},
        {"architecture": "residual", "benchmark": "demo", "onnx": "c.onnx", "node_types": ["Add", "Relu"], "n_params": 1000},
    ])


def test_cli_arguments_are_normalized(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["cli", "--inarc", "Residual, fullyconnected", "--innode", " ReLU ", "--exnode", "all"])
    args = generator.get_args_as_dict(generator.init_parser())
    assert args["inarc"] == ["residual", "fullyconnected"]
    assert args["innode"] == ["relu"]
    assert "relu" not in args["exnode"]


def test_dataframe_filters_architecture_nodes_and_parameters():
    args = {"inarc": ["residual"], "exarc": [], "inbench": [], "exbench": [],
            "innode": ["relu"], "exnode": [], "min_par": 500, "max_par": 1500}
    result = generator.filter_dataframe(metadata_frame(), args)
    assert result["onnx"].tolist() == ["c.onnx"]


def test_empty_filter_lists_are_noops():
    frame = metadata_frame()
    assert len(generator.keep_architectures(frame, [])) == len(frame)
    assert len(generator.remove_nodes(frame, [])) == len(frame)


def test_parameter_filter_with_reversed_bounds_is_noop():
    frame = metadata_frame()
    result = generator.param_range_filter(frame, 100, 10)
    assert result["onnx"].tolist() == frame["onnx"].tolist()


def test_instances_path_uses_repository_root(monkeypatch, tmp_path):
    root = tmp_path / "repo"
    instance_dir = root / "convolutional_benchmarks_vnncomp" / "demo"
    instance_dir.mkdir(parents=True)
    instance_file = instance_dir / "instances.csv"
    instance_file.write_text("a.onnx,p.vnnlib,10\n")
    monkeypatch.setattr(generator, "BENCHMARKS_VNNCOMP_DIR", str(root))
    row = pd.Series({"architecture": "convolutional", "benchmark": "demo"})
    assert generator.get_instances_path(row) == str(instance_file)


def test_result_filter_known_and_specific(monkeypatch, tmp_path):
    expected = tmp_path / "expected.csv"
    expected.write_text("onnx,vnnlib,result\na.onnx,p.vnnlib,sat\nb.onnx,q.vnnlib,unsat\n")
    monkeypatch.setattr(generator, "EXPECTED_RESULTS_FILE", str(expected))
    instances = [{"onnx": "a.onnx", "vnnlib": "p.vnnlib"}, {"onnx": "b.onnx", "vnnlib": "q.vnnlib"}]
    assert len(generator.filter_instances_by_result(instances, "known")) == 2
    assert generator.filter_instances_by_result(instances, "sat") == [instances[0]]


def test_sampling_limits_each_network(monkeypatch):
    monkeypatch.setattr(generator.random, "sample", lambda values, count: values[:count])
    instances = ([{"onnx": "a", "vnnlib": str(i)} for i in range(3)] +
                 [{"onnx": "b", "vnnlib": str(i)} for i in range(2)])
    assert len(generator.sample_instances(instances, 2)) == 4


def test_output_writer_creates_csv_and_preserves_optional_timeout(tmp_path):
    args = {"outdir": str(tmp_path / "nested"), "outname": "result.csv"}
    rows = [{"rel_path_to_onnx": "a.onnx", "rel_path_to_property.vnnlib": "p.vnnlib", "timeout": "10"},
            {"rel_path_to_onnx": "b.onnx", "rel_path_to_property.vnnlib": "q.vnnlib", "timeout": None}]
    generator.write_output_file(args, rows)
    assert (tmp_path / "nested" / "result.csv").read_text() == "a.onnx,p.vnnlib,10\nb.onnx,q.vnnlib\n"


def test_cli_delegates_to_shared_generator(monkeypatch):
    captured = {}
    monkeypatch.setattr(sys, "argv", ["cli", "--outdir", ".", "--outname", "demo.csv"])
    monkeypatch.setattr("cli_gen_instances.generate_instances", lambda args: captured.setdefault("args", args) or [])
    cli_main()
    assert captured["args"]["outname"] == "demo.csv"


def test_gui_logic_caches_metadata_loads(monkeypatch, tmp_path):
    dataset = tmp_path / "nns.csv"
    calls = []
    monkeypatch.setattr("GUI_gen_instance.logic.load_nns_dataframe", lambda path: calls.append(path) or metadata_frame())
    controller = GuiLogic(path_to_input_dataset=str(dataset), possible_origins=["demo", "other"])
    controller.reset_filters()
    controller.reset_filters()
    assert calls == [str(dataset)]

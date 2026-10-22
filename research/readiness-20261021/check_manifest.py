"""Check original preparation evidence through exact participation snapshots."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('participation_history',ROOT/'research/participation-20261022/verify.py')
history=importlib.util.module_from_spec(spec)
spec.loader.exec_module(history)
history.check_manifest(Path(__file__).with_name('manifest.json'))

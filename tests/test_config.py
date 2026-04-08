"""Offline tests for models.toml parsing and validation."""

import argparse
import unittest
from pathlib import Path


def _load():
    from installer.config import load_config
    ns = argparse.Namespace(
        models_toml=None, prune=False, dry_run=True, host="0.0.0.0", port=8000,
    )
    return load_config(ns)


class TestConfigLoading(unittest.TestCase):

    def test_loads_without_error(self):
        config = _load()
        self.assertGreater(len(config.models), 0)

    def test_every_model_has_source(self):
        """Every model must specify either file or include."""
        config = _load()
        for model in config.models:
            with self.subTest(model=model.id):
                self.assertTrue(
                    model.file or model.include,
                    f"{model.id}: must have 'file' or 'include'",
                )

    def test_every_model_has_at_least_one_profile(self):
        config = _load()
        for model in config.models:
            with self.subTest(model=model.id):
                self.assertGreater(
                    len(model.profiles), 0,
                    f"{model.id}: no profiles defined",
                )

    def test_no_duplicate_profile_names(self):
        config = _load()
        names = []
        for model in config.models:
            for profile in model.profiles:
                names.append(profile.name)
        self.assertEqual(len(names), len(set(names)), f"Duplicate profile names: {names}")

    def test_large_models_use_include(self):
        """Large models should use include (multi-shard), not a single file."""
        config = _load()
        for model in config.models:
            if model.large:
                with self.subTest(model=model.id):
                    self.assertIsNotNone(
                        model.include,
                        f"{model.id}: large=true but no include pattern",
                    )

    def test_local_dirs_are_unique(self):
        config = _load()
        dirs = [m.local_dir for m in config.models]
        self.assertEqual(len(dirs), len(set(dirs)), f"Duplicate local_dir values")

    def test_profile_ctx_size_positive(self):
        config = _load()
        for model in config.models:
            for profile in model.profiles:
                with self.subTest(profile=profile.name):
                    self.assertGreater(profile.ctx_size, 0)


if __name__ == "__main__":
    unittest.main()

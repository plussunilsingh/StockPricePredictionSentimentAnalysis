CHANGELOG - Pairwise Humanization Edits

v0.1 - Humanization pass

- Pair 01: `AppConfig.py`, `best_model.py`
  - Added module and function docstrings, improved logging, created default logs directory, and added defensive JSON parsing.
  - Added docstrings and minor API helper (`load_default`) to RF wrapper for clarity.

- Pair 02: `data_factory.py`, `sentiment_analyzer.py`
  - Reworked factory wrapper to adapt to `DataScannerFactory`.
  - Updated sentiment analyzer to use local `nltk_data`, added robust fallbacks and logging.

- Pair 03: `lstm_model.py`, `trainer.py`
  - Documented LSTM wrapper, added simulation fallback when TF not available, and prepared data helpers.

- Pair 04: `DataMapper.py`, `preprocessing.py`
  - Centralized mapping utilities and clarified pre-processing steps.

- Pair 05: package `__init__` files
  - Added brief package docstrings to clarify structure.

- Pair 06: `PredictionDTO.py`, `frontend/app.py`
  - Documented DTO schemas and improved frontend defensive handling and docstrings.

- Pair 07: frontend `__init__` and `scripts/generate_data.py`
  - Added package docstring and documented synthetic data generator.

- Pair 08: `scripts/train_models.py`
  - Documented training orchestration and added defensive checks.

Notes:
- All edits were intentionally small and low-risk: docstrings, comments, defensive checks and non-breaking refactors.
- Suggest committing each pair as an individual commit to create a transparent development history.


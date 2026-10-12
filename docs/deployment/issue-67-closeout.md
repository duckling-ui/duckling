# Issue #67 closeout notes

Tracking: [duckling-ui/duckling#67](https://github.com/duckling-ui/duckling/issues/67)

| ID | Mitigation |
|----|------------|
| A | `frontend/Dockerfile` pins `nginxuser` UID 1000; `docker-compose.prebuilt.yml` / `docker-compose.prod.yml` tmpfs use `uid=1000,gid=1000,mode=0755` for `/var/cache/nginx` and `/var/run` |
| B | `backend/entrypoint.sh` forces 1 Gunicorn worker for `DUCKLING_ENGINE_KIND=local`; jobs marked `processing` in history; status fallback messages fixed |
| C | Converter uses `TesseractCliOcrOptions`; settings check probes `tesseract` binary (not `tesserocr`) |
| D | `TESSERACT_LANGUAGE_MAP` maps `en`→`eng`, `ru`→`rus`, etc.; supports `en+ru` |
| E | Default `ocr.allow_fallback_without_ocr=false` (fail closed); opt-in fallback sets `ocr_warning`; status/result expose `ocr_backend_used` |

Suggested issue comment after merge:

```text
Fixed in <PR-URL> (branch fix/issue-67-prebuilt-runtime):

- A: nginx tmpfs owned by UID 1000 for non-root frontend
- B: one Gunicorn worker for local engine + processing history/status messaging
- C: Tesseract via TesseractCliOcrOptions (CLI), not tesserocr
- D: UI language → traineddata mapping (en→eng, ru→rus)
- E: OCR fail-closed by default; allow_fallback_without_ocr opt-in
```

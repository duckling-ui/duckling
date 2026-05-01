from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent


def _read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_frontend_dockerfile_runs_as_non_root():
    dockerfile = _read("frontend/Dockerfile")
    assert "USER nginxuser" in dockerfile
    assert "FROM nginx:1.29-alpine3.22 AS production" in dockerfile


def test_prod_compose_has_restricted_runtime_defaults():
    compose = _read("docker-compose.prod.yml")
    assert "read_only: true" in compose
    assert "cap_drop:" in compose
    assert "- ALL" in compose
    assert "no-new-privileges:true" in compose
    assert "tmpfs:" in compose


def test_publish_workflow_has_security_gates():
    workflow = _read(".github/workflows/publish-docker.yml")
    assert "id-token: write" in workflow
    assert "aquasec/trivy:" in workflow
    assert "--severity HIGH,CRITICAL --exit-code 1" in workflow
    assert "cosign sign --yes" in workflow
    assert "syft " in workflow


def test_tests_workflow_rehearses_publish_docker_scan_gates():
    workflow = _read(".github/workflows/test.yml")
    assert "Docker publish rehearsal (PR gate)" in workflow
    assert "--platform linux/amd64" in workflow
    assert "--sbom" in workflow
    assert "--provenance" in workflow
    assert "Install Trivy CLI" in workflow
    assert "sudo apt-get install -y trivy" in workflow
    assert "docker save -o trivy-images/duckling-backend-${{ steps.version.outputs.version }}.tar" in workflow
    assert "docker save -o trivy-images/duckling-frontend-${{ steps.version.outputs.version }}.tar" in workflow
    assert "--input trivy-images/duckling-backend-${{ steps.version.outputs.version }}.tar" in workflow
    assert "--input trivy-images/duckling-frontend-${{ steps.version.outputs.version }}.tar" in workflow


def test_backend_config_uses_writable_db_path_for_docker():
    config = _read("backend/config.py")
    assert 'DATA_FOLDER = Path("/app/data")' in config
    assert "DATABASE_PATH = DATA_FOLDER / \"history.db\"" in config


def test_backend_requirements_pin_cve_fixes_for_image_scans():
    requirements = _read("backend/requirements.txt")
    assert "jaraco.context==6.1.0" in requirements
    assert "wheel==0.46.2" in requirements


def test_backend_dockerfile_enforces_cve_fix_versions():
    dockerfile = _read("backend/Dockerfile")
    assert 'pip install --upgrade --force-reinstall --no-deps "jaraco.context==6.1.0" "wheel==0.46.2"' in dockerfile
    assert 'assert_min("jaraco.context", "6.1.0")' in dockerfile
    assert 'assert_min("wheel", "0.46.2")' in dockerfile
    assert "remove_legacy_metadata(" in dockerfile
    assert "remove_legacy_ensurepip_wheels(" in dockerfile


def test_docker_build_script_forces_plain_progress_logging():
    script = _read("scripts/docker-build.sh")
    assert "export BUILDKIT_PROGRESS=plain" in script
    assert "run_cmd()" in script
    assert "docker buildx build \\" in script
    assert "--progress=plain \\" in script
    assert "--platform)" in script
    assert "DUCKLING_BUILD_PLATFORMS" in script
    assert "if [ \"$ENABLE_SBOM\" = true ]" in script
    assert "if [ \"$ENABLE_PROVENANCE\" = true ]" in script
    assert "if [ \"$PUSH\" = true ]" in script
    assert "${ENABLE_SBOM:+--sbom=true}" not in script
    assert "${ENABLE_PROVENANCE:+--provenance=true}" not in script
    assert "${PUSH:+--push}" not in script
    # macOS /bin/bash 3.2: "${arr[@]}" with set -u errors when arr is empty; use ${arr[@]+"${arr[@]}"}
    assert 'BUILDX_FLAGS[@]+"${BUILDX_FLAGS[@]}"' in script
    assert 'BUILDX_OUTPUT_FLAGS[@]+"${BUILDX_OUTPUT_FLAGS[@]}"' in script
    assert "--load is incompatible with --sbom/--provenance" in script
    assert "disabling attestations for local image load" in script

from pathlib import Path


PROJECT_ROOT = Path(__file__).parent.parent


def _read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def test_frontend_dockerfile_runs_as_non_root():
    dockerfile = _read("frontend/Dockerfile")
    assert "USER nginxuser" in dockerfile
    assert "FROM nginx:1.29-alpine3.22 AS production" in dockerfile
    assert "RUN apk upgrade --no-cache" in dockerfile


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
    assert "Install Trivy CLI" in workflow
    assert "sudo apt-get install -y trivy" in workflow
    assert "trivy image --severity HIGH,CRITICAL --exit-code 1 --ignore-unfixed --scanners vuln" in workflow
    assert "docker run --rm aquasec/trivy" not in workflow
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
    assert "jaraco.context>=6.1.0" in requirements
    assert "wheel>=0.46.2" in requirements

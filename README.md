# jstack

**필요한 만큼 탐색하고, 실제 결과로 검증하는 AI 코딩 워크플로.**

[한국어](README.md) · [English](README.en.md)

[![검증](https://github.com/promptprobe/jstack/actions/workflows/validate.yml/badge.svg)](https://github.com/promptprobe/jstack/actions/workflows/validate.yml)
[![MIT 라이선스](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![스킬 다운로드](https://img.shields.io/badge/skill-ZIP_download-green.svg)](https://github.com/promptprobe/jstack/releases/download/v0.2.0/jstack-mode.zip)

jstack은 **Codex와 Claude Code에 폴더만 넣으면 바로 사용하는 AI 코딩 스킬**입니다. 대화에서 한 번 활성화하고 원하는 결과와 작업 강도를 정하면, 작업에 맞는 플레이북으로 진행하고 실제 확인한 근거를 보고합니다.

**기본 사용에는 Python, Git clone, 설치 명령, 설정 파일이 필요 없습니다.** 진입 스킬 하나와 작업별 플레이북 여덟 개가 ZIP 안에 들어 있습니다. 작업 대상 프로젝트 자체의 테스트에 필요한 실행 환경은 별개입니다. 호스트에서 에이전트를 실행할 때 모델 사용량은 발생합니다.

현재 **0.2.0 초기 버전**입니다. 스킬 단독 사용이 기본이며, 검증 기록 저장·재시도 제한·소스 변경 감지가 필요할 때만 별도 Python 도구를 선택합니다. 실제 확인한 범위와 한계는 [검증 기록](docs/validation.ko.md)에 구분합니다.

```text
사용자: $jstack-mode cheap
        재연결 후 장바구니 상품이 중복으로 추가되는 버그를 고쳐줘.

에이전트: 완료 기준 설정 → 버그 재현 → 수정 → 검증 → 근거 보고

사용자: 두 번 연속 재연결하는 경우도 확인해줘.

에이전트: 같은 jstack 세션과 작업 강도를 유지하며 후속 작업 진행

사용자: jstack off

에이전트: 이 대화에서 jstack 모드 해제
```

Claude Code에서는 `$jstack-mode` 대신 **`/jstack-mode`**를 사용합니다. 위 대화는 사용 예시이며, 모든 모델이 항상 동일한 순서로 행동한다는 보장은 아닙니다.

<a id="install-in-a-project"></a>

## 스킬 ZIP 받아 바로 시작하기

1. **[jstack-mode.zip 다운로드](https://github.com/promptprobe/jstack/releases/download/v0.2.0/jstack-mode.zip)** 후 압축을 풉니다.
2. 안에 있는 **`jstack-mode` 폴더 전체**를 아래 위치 중 하나에 넣습니다. `SKILL.md`만 따로 옮기지 마세요.
3. Codex 또는 Claude Code에서 스킬을 호출합니다. 목록에 안 보이면 호스트를 새로고침하거나 재시작하세요.

| 도구 | 모든 프로젝트에서 사용 — 개인 설치 | 이 프로젝트만 — 프로젝트 설치 | 호출 |
| --- | --- | --- | --- |
| Codex | `~/.agents/skills/jstack-mode/` | `.agents/skills/jstack-mode/` | `$jstack-mode cheap` |
| Claude Code | `~/.claude/skills/jstack-mode/` | `.claude/skills/jstack-mode/` | `/jstack-mode cheap` |

개인 설치와 프로젝트 설치 중 하나를 선택하세요. 둘 다 쓰면 같은 ZIP의 폴더를 각 호스트 위치에 복사하면 됩니다. `~`는 사용자 홈 폴더입니다. 폴더가 없으면 만들고, 최종 경로가 `.../skills/jstack-mode/SKILL.md`인지 확인하세요. 기존 동명의 스킬이 있다면 사용자 수정본을 백업한 뒤 교체하세요.

```text
# Codex 대화
$jstack-mode normal
이 프로젝트의 로그인 오류를 재현하고 수정한 뒤 검증해줘.

# Claude Code 대화
/jstack-mode normal
이 프로젝트의 로그인 오류를 재현하고 수정한 뒤 검증해줘.
```

**여기까지면 기본 사용 준비가 끝납니다.** `setup`이나 `doctor`를 실행할 필요가 없습니다. 스킬은 프로젝트 지침·테스트 파일·실행 명령을 살펴 적절한 검증을 선택합니다. 검증할 수 없는 환경이면 확인하지 못한 부분을 보고하며, 자동으로 통과 처리하지 않습니다.

스킬 복사만으로 `AGENTS.md`, `CLAUDE.md`, `.gitignore` 또는 `.jstack/`를 만들거나 변경하지 않습니다. 설치 자체가 모드를 켜지도 않습니다. 같은 대화에서는 유지하고 새 대화에서 다시 호출합니다. 설치 위치는 [OpenAI 공식 안내](https://learn.chatgpt.com/docs/build-skills)와 [Claude Code 공식 안내](https://code.claude.com/docs/en/skills)를 따릅니다.

[스킬 원본 폴더](skills/jstack-mode) · [ZIP 체크섬](https://github.com/promptprobe/jstack/releases/download/v0.2.0/SHA256SUMS) · [설치·업데이트·삭제 안내](docs/installation.md)

### 선택 기능: 검증 기록을 파일로 남기기

| 기능 | 스킬만 사용 — 기본 | 선택형 로컬 도구 |
| --- | --- | --- |
| 작업 분류·예산·대화 모드 유지 | 지원, 에이전트 지침으로 동작 | 지원 |
| 프로젝트 테스트 실행·결과 설명 | 호스트 도구로 실행 | 검사 명령과 결과를 파일로 기록 |
| 설정 파일·세션 ID | 필수 아님 | 필요 |
| 재시도 제한·검증 후 소스 변경 감지 | 에이전트가 판단, 강제하지 않음 | 작업별 제한·Git 소스 식별값 비교 |
| 추가 실행 환경 | jstack 자체는 없음 | Python 3.10+ 및 Git |

기존 `.jstack/config.json`이 있으면 작업 강도·검증 명령 등에 참고할 수 있지만 기본 사용에는 필요 없습니다. 자동 기록을 원할 때만 [선택형 도구 설치](docs/installation.md#optional-recorded-operation)와 [설정 안내](docs/configuration.md)를 따르세요. 도구 설치 후에도 기본은 스킬 단독 모드입니다. 에이전트에게 **“jstack 로컬 기록 모드로 진행해줘”**라고 요청하면 기록 도구를 사용합니다.

## 작업 강도: cheap · normal · deep

| 단계 | 탐색 횟수 지침¹ | 첫 검증 후 수정·재시도² | 하위 에이전트 상한³ | 처음 읽을 파일 수 지침¹ |
| --- | ---: | ---: | ---: | ---: |
| `cheap` | 1 | 1 | 0 | 4 |
| `normal` | 2 | 2 | 1 | 10 |
| `deep` | 4 | 3 | 3 | 20 |

¹ 에이전트에게 주는 지침입니다. 호스트의 도구 호출을 기술적으로 제한하지는 않습니다.

² 스킬 단독 모드에서는 지침입니다. 선택형 로컬 도구를 사용할 때만 작업별로 최초 최종 검증 1회와 해당 횟수만큼의 재시도를 강제합니다.

³ 설정에 상한이 있으면 더 낮은 값을 따릅니다. 병렬 에이전트는 **기본적으로 꺼져 있으며**, 사용자 또는 기존 설정의 명시적 활성화와 호스트 권한이 필요합니다.

표의 숫자는 채워야 할 할당량이 아니라 상한입니다. `cheap`에서는 탐색과 조율을 줄이되 필수 검증을 생략하지 않습니다. `deep`에서는 더 깊이 조사할 수 있지만, 여러 에이전트를 반드시 띄우지는 않습니다. 현재 호스트의 모델을 유지하며 작업 강도나 유료 모델을 자동으로 올리지 않습니다.

**토큰·금액을 측정하거나 청구액 상한을 강제하는 기능은 아직 없습니다.** `cheap`도 호스트의 모델·추론 강도나 다른 플러그인의 문맥 크기를 자동으로 바꾸지 않습니다. 필요한 지침만 읽고, 변경과 관련된 파일을 살펴보고, 불필요한 반복을 줄여 비용을 낮추는 것이 설계 목표입니다. 실제 절감률은 비교 측정 전이므로 주장하지 않습니다. [비용 관리 원칙](docs/cost-control.md)

## 작업별 플레이북

| 플레이북 | 사용하는 상황 | 확인할 근거 |
| --- | --- | --- |
| `feature` | 새로운 기능 추가 | 사용 흐름과 관련 실패 사례의 실제 동작 |
| `bug-fix` | 버그 수정 | 수정 전 실패 재현과 수정 후 회귀 테스트 |
| `refactor` | 동작을 유지하면서 구조 개선 | 변경 전후 동일한 동작을 확인하는 검사 |
| `perf` | 성능 개선 | 동일 조건의 측정값과 기능 정상 여부 |
| `prototype` | 아이디어·가설 검토 | 제한된 실험 결과와 실제 사용을 위한 남은 작업 |
| `verification` | 변경·산출물 검증 | 직접 확인한 사실과 확인하지 못한 조건 |
| `shipping` | 승인된 공개·배포 작업 | 원격 커밋, CI, 실제 배포 상태를 각각 확인 |
| `lightweight` | 문구·간격 등 작은 수정 | 수정된 결과 확인 또는 관련 기존 검사 |

해당 작업의 플레이북만 읽도록 설계했습니다. 선택형 CLI의 자동 분류는 간단한 한국어·영어 키워드 방식이라 문맥을 오해할 수 있습니다. 에이전트는 작업 의도를 판단하고 필요하면 `--playbook`으로 바로잡아야 합니다. 플레이북 선택만으로 공개·배포 명령이 실행되지는 않습니다.

Codex 사용 예시입니다. Claude Code에서는 `$`를 `/`로 바꿔 사용하세요.

```text
$jstack-mode normal
CSV 내보내기를 추가해줘. 내려받은 파일을 다시 열었을 때
행 수와 한글 이름이 그대로 유지돼야 해.

$jstack-mode cheap
빈 화면 안내 문구를 수정하고 모바일 너비에서도 확인해줘.

$jstack-mode deep
같은 데이터로 반복 측정하면서 검색 지연을 줄여줘.
검색 결과의 순서는 유지해야 해.

$jstack-mode normal
코드는 수정하지 말고 이 PR을 검증해줘.
저장된 결과물을 확인하고 검증하지 못한 부분도 알려줘.
```

### 한 번 켜면 언제까지 유지되나요?

**같은 대화 안에서 유지하도록 설계했습니다.** 기본 모드에서는 활성 상태와 작업 강도를 대화 문맥에 기억합니다. 세션 ID나 디스크 기록을 만들지 않습니다.

- `jstack off`: 현재 대화의 모드 해제
- `jstack budget cheap`: 현재 대화의 작업 강도 변경
- 새 대화: 스킬을 다시 호출

상시 실행 서비스나 전역 활성 상태는 없습니다. 대화가 요약되거나 문맥이 사라질 때 상태를 유지하는지는 호스트의 동작에 달려 있습니다. 문맥을 잃으면 스킬을 다시 호출하세요. **호스트 차원의 영구 기억을 보장하지 않습니다.** 선택형 기록 모드에서만 세션 ID가 생기며, 그 ID도 호스트가 기억해야 후속 작업에 이어 쓸 수 있습니다.

## 선택형 로컬 도구 직접 실행하기

별도로 설치·설정한 로컬 도구는 다음처럼 직접 사용할 수 있습니다. 스킬 단독 사용자에게는 필요 없는 단계입니다.

```sh
python3 .jstack/jstack.py mode on --host codex --budget cheap
# 출력된 세션 ID를 아래 SESSION_ID에 입력

python3 .jstack/jstack.py plan '재연결 후 상품 중복 추가 버그 수정' \
  --session SESSION_ID --playbook bug-fix \
  --accept '재연결 후 한 번 클릭하면 상품이 하나만 추가된다'
# 작업 생성 전에 검증 명령을 설정하고, 출력된 작업 ID를 아래 TASK_ID에 입력

python3 .jstack/jstack.py verify --task TASK_ID --phase baseline
# 수정 전 실패는 재현 근거가 됩니다. 이후 코드를 수정합니다.

python3 .jstack/jstack.py verify --task TASK_ID
python3 .jstack/jstack.py report --task TASK_ID
python3 .jstack/jstack.py report --task TASK_ID --format json
```

검증 기록에는 실행 명령, 종료 코드, 소요 시간, 출력의 마지막 부분, 실행 전후 소스의 식별값이 남습니다. 검증 이후 Git이 추적하거나 무시하지 않은 파일이 달라지면 이전 결과를 **오래된 결과**로 표시합니다. 최신 검증이 실패했는데 과거의 성공 기록으로 통과했다고 보여주지 않습니다.

검증 항목이 없거나, 실행 파일을 찾지 못하거나, 제한 시간이 지나거나, 검사 도중 소스가 바뀌면 `local_checks_passed`로 처리하지 않습니다. 다만 이 상태도 해당 명령의 검사 범위를 통과했다는 뜻이며, 기능 전체의 완성이나 배포 성공을 자동으로 뜻하지는 않습니다.

실행 화면, CI, 배포 결과 등 추가 근거는 `evidence`로 기록할 수 있습니다. 직접 입력한 주장은 **사용자가 제공한 관찰**로 구분하며, 도구가 독립적으로 검증한 사실로 바꾸지 않습니다. 자연어 완료 기준은 자동 판정하지 않고, 로컬 JSON 기록은 서명된 증명서가 아닙니다. [명령·근거 기록 상세](docs/cli.md)

## 구조

```mermaid
flowchart LR
  A[스킬 ZIP] --> B[Codex 또는 Claude Code]
  B --> C[필요한 플레이북만 읽기]
  C --> D[호스트가 수정하고 검증]
  D --> E[대화에서 근거 보고]
  D -. 기록 모드 선택 시 .-> F[로컬 Python 도구]
  F --> G[검증 기록과 소스 변경 감지]
```

```text
skills/jstack-mode/       공통 진입 스킬과 작업별 플레이북
adapters/                Codex·Claude Code별 안내
jstack_core/             설정, 설치, 작업 분류, 세션, 검증, 보고
jstack.py                실행 진입점
tests/                   설치·상태·검증 관련 회귀 테스트
scripts/                 스킬 ZIP 빌드·검증·전체 흐름 테스트
docs/                    설치, 구조, 비용 원칙, 상세 문서
```

호스트는 판단·코드 수정·필요한 에이전트 실행을 담당합니다. 선택형 로컬 도구는 기록 모드의 작업 규칙과 검증 기록을 담당하며, 직접 모델을 호출하거나 배포·커밋·푸시하지 않습니다. pstack이나 Cursor에 대한 실행 의존성도 없습니다. [구조와 검증 범위](docs/architecture.md)

## 테스트와 기여

```sh
python3 scripts/validate.py
```

단위·통합 테스트, 설치된 CLI의 전체 흐름, Python 문법, 독립 스킬 ZIP과 두 호스트 복사 경로, 문서 내부 링크를 확인합니다. CI는 Linux·macOS·Windows와 여러 Python 버전을 대상으로 실행합니다. **CI 통과는 도구 테스트의 근거이며, 모든 호스트에서의 모델 행동이나 토큰 절감까지 증명하지는 않습니다.**

실제로 확인한 환경과 결과는 [한국어 검증 기록](docs/validation.ko.md)을 참고하세요. 기여 방법과 실제 호스트 평가 시나리오는 [기여 안내](CONTRIBUTING.md), 보안 관련 제보 방법은 [보안 안내](SECURITY.md)에 있습니다. 그 밖의 상세 기술 문서는 현재 영문으로 제공됩니다.

## 현재 한계와 다음 단계

- **실제 호스트 평가:** 버그 수정, 후속 요청, 모드 해제, 대화 요약 후 복구를 반복 검증합니다. 설치 테스트와 실제 모델의 지침 준수 여부는 구분합니다.
- **실제 비용 측정:** 사용자가 선택한 경우 호스트 사용량을 가져와 비용과 결과 품질을 함께 비교합니다. 청구액을 확실히 제한하려면 호스트 지원이 필요합니다.
- **검증 범위 확장:** 현재 식별값은 무시된 파일, 외부 서비스, 환경 변화까지 포괄하지 않습니다. 선택한 외부 입력, CI 결과, 브라우저 산출물을 연결하고 서브모듈 지원도 추가할 예정입니다.
- **배포 편의:** 독립 스킬 ZIP과 SHA-256 체크섬을 제공합니다. 이후 호스트별 플러그인 패키징과 서명된 체크섬을 검토합니다. npm·PyPI 패키지는 아직 배포하지 않았습니다.
- **작업 분류 개선:** 문맥이 모호하거나 여러 언어가 섞인 사례로 분류 품질을 평가합니다. 사용자의 명시적 선택을 유지하고, 단순 분류만을 위해 모델 호출을 추가하지 않습니다.

구체적인 완료 기준은 [로드맵](docs/roadmap.md)에 정리했습니다.

## 영감과 라이선스

제가 좋아하는.. Lauren Tan([poteto](https://github.com/poteto))의 [pstack](https://github.com/cursor/plugins/tree/main/pstack)에서 대화에 유지되는 엔지니어링 모드, 작업별 플레이북, 근거 중심의 검증이라는 개념에 영감을 받았습니다.

jstack의 코드, 프롬프트, 구조, 작업 강도 정책과 문서는 이 프로젝트를 위해 독립적으로 작성했습니다. pstack의 포크나 공식 연동 프로젝트는 아닙니다. pstack에도 추론 예산 설정이 있으므로 예산 선택을 jstack만의 발명이라고 주장하지 않으며, 비용이 더 적게 든다는 비교 결과도 아직 없습니다. [설계 출처](docs/provenance.md)

[MIT 라이선스](LICENSE) © 2026 promptprobe.

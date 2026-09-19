# Inyoung Media

주제별 미디어 허브형 Jekyll 사이트입니다.

- **허브(`/`)**에서 주제 채널로 이동
- **주제 페이지**에서 추천 글 + 이미지·제목 목록(페이지네이션)
- **글**은 Markdown, 대표 이미지·동영상 링크 지원
- **검색**은 `/search.json` 기반 클라이언트 검색

## 로컬에서 확인하기

### 1. Ruby 준비

Windows: [RubyInstaller](https://rubyinstaller.org/downloads/) **Ruby+Devkit** (3.2+) 설치 후 `ridk install`  
확인:

```powershell
ruby -v
gem -v
```

### 2. 의존성 설치

```powershell
cd d:\works\inyounglee.github.io
gem install bundler
bundle install
```

### 3. 개발 서버

```powershell
bundle exec jekyll serve --livereload
```

- http://127.0.0.1:4000
- 주제 예: http://127.0.0.1:4000/blackdesert/

`index.html`을 파일로 직접 열지 말고, 위 주소로 접속하세요.

| 명령 | 설명 |
| --- | --- |
| `bundle exec jekyll serve --livereload` | 로컬 미리보기 |
| `bundle exec jekyll serve --port 4001` | 포트 변경 |
| `bundle exec jekyll build` | `_site` 빌드 |

## 콘텐츠 작성

`_posts/`에 Markdown 파일을 추가합니다. 파일명: `YYYY-MM-DD-slug.md`

```markdown
---
layout: post
title: "글 제목"
categories: [blackdesert]
image: /assets/images/posts/kharazad-reform.svg
featured: true
---

본문은 **Markdown**으로 작성합니다.
```

현재 주제는 `_data/topics.yml`의 **검은사막** (`blackdesert`) 하나뿐입니다.

| 항목 | 설명 |
| --- | --- |
| `categories` | 주제 slug (`blackdesert`) |
| `image` | 목록·상세 대표 이미지 (원작 SVG 권장) |
| `featured` | `true`면 해당 주제 페이지 상단 **추천 글**에 노출 |
| `video` / `video_embed` | 선택. 링크 버튼과 iframe |

## 주제별 추천 글 바꾸기

주제 페이지(예: `/blackdesert/`, 화면의 **검은사막**) 상단 **추천 글**은 글 front matter의 `featured`로 고릅니다.

1. `_posts/`에서 해당 주제 글(`categories`가 주제 slug와 같음)을 연다.
2. 추천에 넣을 글은 `featured: true`, 빼려면 `featured: false` 또는 항목을 삭제한다.
3. 같은 주제에 `featured: true`인 글이 여러 개면 **날짜가 최신인 글부터 최대 4개**가 가로로 나열된다.

검은사막 예시:

```markdown
---
categories: [blackdesert]
featured: true    # /blackdesert/ 추천 글에 표시
---
```

현재 검은사막 추천 글은 `2026-08-15-hyper-boost-equipment-guide.md` 한 편만 `featured: true`입니다.

표시 개수(기본 4)를 바꾸려면 `_includes/featured.html`의 `limit: 4`를 수정합니다.

## 포스트 아이템명 → 제작 계산기 링크

포스트 본문의 검은사막 아이템명은 빌드 시 [제작 계산기](https://bdo-craft-calc.inyounglee.kr/)로 연결됩니다.

- 링크 형식: `https://bdo-craft-calc.inyounglee.kr/kr/items/{아이템명slug}` (공백 → `-`)
- 이름 목록: `_data/bdo_craft_items.json`
- 링크 적용: `_plugins/bdo_craft_item_links.rb` (Jekyll이 포스트 HTML을 만들 때)

새 글에 기존 목록에 없는 아이템명이 들어가면, 저장소 루트에서 목록을 다시 만듭니다. **Python 3.10+** 와 네트워크가 필요합니다.

```powershell
python auto/script/build-bdo-item-links.py
python auto/script/build-bdo-item-links.py --help
```

갱신 뒤에는 `bundle exec jekyll serve` 또는 `bundle exec jekyll build`로 사이트를 다시 빌드합니다. GitHub Pages 배포는 커밋된 `_data/bdo_craft_items.json`만 쓰고, 이 스크립트는 CI에서 돌리지 않습니다.

### 카탈로그에서 아이템명을 가져오는 동작

스크립트는 제작 계산기 사이트 HTML을 긁지 않습니다. 계산기가 쓰는 **Supabase 아이템 마스터** `paz_items`를 REST로 읽습니다.

1. `GET https://yjswbueufqddkbgwxlul.supabase.co/rest/v1/paz_items` 에 `name`만 요청합니다.
2. 이벤트·지식·강화 키 등 제외 행(`exclude`가 있는 행), 이름 `[이벤트]` 접두, 비정상 `item_id`는 빼 둡니다.
3. 한 번에 1,000개씩 `Range`로 끝까지 받아 고유 이름을 모읍니다.
4. `_posts/*.md` 본문(프론트매터·코드·이미지 제외)에 **실제로 등장하는 이름만** 남깁니다. `[공헌도] 그믐달 울타리`처럼 접두가 있는 항목은 본문의 `그믐달 울타리`에도 맞춥니다.
5. 짧은 일반어·스탯 문구는 빼고, 결과를 `_data/bdo_craft_items.json`에 덮어씁니다.

이 JSON이 있어야 플러그인이 링크를 걸 수 있습니다. 사이트 런타임은 계산기 API를 호출하지 않습니다.

### `BDO_CRAFT_SUPABASE_ANON_KEY`

제작 계산기 Supabase 프로젝트의 **anon / publishable 키**(공개 읽기용)입니다. 서비스 롤 키가 아닙니다.

| 항목 | 내용 |
| --- | --- |
| 무엇 | `paz_items`를 익명으로 `SELECT`할 때 쓰는 API 키. 계산기 프론트엔드의 `VITE_SUPABASE_PUBLISHABLE_KEY`와 같은 종류입니다. |
| 어디서 쓰나 | **오직** `auto/script/build-bdo-item-links.py`의 HTTP 헤더 `apikey`, `Authorization: Bearer …`. Jekyll 빌드·GitHub Pages·브라우저 JS에는 쓰이지 않습니다. |
| 없어도 되나 | 선택. 비어 있으면 스크립트에 넣어 둔 기본 키를 씁니다. 계산기 프로젝트가 키를 바꾸면 환경 변수로 덮어씁니다. |
| 키를 받는 곳 | 계산기 Supabase 대시보드 → **Project Settings → API → Project API keys** 의 `anon` `public` (또는 publishable). |

현재 PowerShell 세션에만 설정:

```powershell
$env:BDO_CRAFT_SUPABASE_ANON_KEY = "sb_publishable_...."
python auto/script/build-bdo-item-links.py
```

Windows 사용자 환경 변수로 유지하려면 시스템 설정 → 환경 변수에 같은 이름으로 넣거나, PowerShell 프로필에 위 한 줄을 추가합니다. GitHub Actions secret으로 넣을 필요는 없습니다. 목록 갱신은 로컬에서 돌린 뒤 JSON을 커밋하면 됩니다.

키를 저장소에 커밋하지 마세요. 스크립트 기본값은 계산기 프론트가 이미 브라우저에 실어 보내는 공개 키와 같고, 테이블 RLS상 읽기만 가능합니다.

## 설정 변경

| 파일 | 역할 |
| --- | --- |
| `_config.yml` → `pagination.per_page` | 목록 페이지당 글 수 (기본 10) |
| `_data/topics.yml` | 허브에 보이는 주제 채널 |
| `blackdesert/index.html` | 검은사막 목록 (`pagination.category: blackdesert`) |

새 주제를 추가할 때:

1. `_data/topics.yml`에 항목 추가
2. `새주제/index.html` 생성 (`pagination.category`를 slug로)
3. `_posts` 글의 `categories`에 동일 slug 지정

## GitHub Pages

이 사이트는 **Jekyll 4 + Bundler**로 빌드합니다. GitHub Pages 화면의 **Jekyll Configure** 템플릿은 쓰지 마세요. 그 템플릿은 `actions/jekyll-build-pages`로 **옛 Jekyll 3.9**를 돌려서 CSS(`@use`)와 `jekyll-paginate-v2`가 깨집니다.

1. **Settings → Pages → Build and deployment → Source** 를 **GitHub Actions** 로 둡니다.
2. 워크플로는 저장소의 `.github/workflows/pages.yml` (**Deploy Jekyll site to Pages**)만 사용합니다.
3. **Actions** 탭에서 해당 워크플로가 초록색인지, **deploy** job까지 끝났는지 확인합니다.
4. 배포 후 https://inyounglee.github.io/assets/css/main.css 를 열었을 때 `@use "tokens"` 가 아니라 `{` `}` 가 있는 CSS여야 합니다.

`main`에 이 변경을 푸시한 뒤 Actions가 성공해야 반영됩니다.

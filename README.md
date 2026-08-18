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

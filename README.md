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
- 주제 예: http://127.0.0.1:4000/travel/

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
categories: [travel]
image: /assets/images/posts/cover-01.svg
featured: true
video: https://www.youtube.com/watch?v=...
video_embed: https://www.youtube.com/embed/...
---

본문은 **Markdown**으로 작성합니다.
```

| 항목 | 설명 |
| --- | --- |
| `categories` | 주제 slug (`_data/topics.yml`과 동일) |
| `image` | 목록·상세 대표 이미지 |
| `featured` | `true`면 주제 상단 추천에 노출 |
| `video` / `video_embed` | 선택. 링크 버튼과 iframe |

## 설정 변경

| 파일 | 역할 |
| --- | --- |
| `_config.yml` → `pagination.per_page` | 목록 페이지당 글 수 (기본 10) |
| `_data/topics.yml` | 허브에 보이는 주제 채널 |
| `travel/index.html` 등 | 주제 목록 페이지 (`pagination.category`) |

새 주제를 추가할 때:

1. `_data/topics.yml`에 항목 추가
2. `새주제/index.html` 생성 (`pagination.category`를 slug로)
3. `_posts` 글의 `categories`에 동일 slug 지정

## GitHub Pages

`main` 푸시 후 **Settings → Pages → Source: GitHub Actions** 로 배포합니다.

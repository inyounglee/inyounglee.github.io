# Inyoung Lee

Jekyll 4로 만든 개인 랜딩 페이지입니다. 다크/라이트 테마, 벤토 그리드, 글래스 헤더를 사용하며 `main`에 푸시하면 GitHub Actions가 GitHub Pages로 배포합니다.

## 로컬에서 페이지 확인하기

수정한 화면을 브라우저에서 바로 보려면 Ruby와 Bundler가 필요합니다. 아래는 Windows(PowerShell) 기준입니다.

### 1. Ruby 설치

1. [RubyInstaller](https://rubyinstaller.org/downloads/)에서 **Ruby+Devkit** (Ruby 3.2 이상, 3.3 또는 4.x)을 받습니다.
2. 설치 중 **MSYS2 개발 도구**를 함께 설치합니다. 설치가 끝나면 `ridk install`이 실행됩니다. 기본값(1, 3)을 선택하면 됩니다.
3. **새 PowerShell**을 열고 버전을 확인합니다.

```powershell
ruby -v
gem -v
```

Ruby 3.2 이상과 RubyGems가 보이면 준비된 것입니다.

> macOS: `brew install ruby`  
> Ubuntu/Debian: `sudo apt install ruby-full build-essential`

### 2. Bundler 설치

```powershell
gem install bundler
```

### 3. 의존성 설치

저장소 루트에서 실행합니다.

```powershell
cd d:\works\inyounglee.github.io
bundle install
```

Jekyll과 플러그인이 설치됩니다. 처음에는 1~2분 정도 걸릴 수 있습니다.

### 4. 개발 서버 실행

```powershell
bundle exec jekyll serve --livereload
```

브라우저에서 아래 주소로 엽니다.

- **http://127.0.0.1:4000**
- 또는 **http://localhost:4000**

HTML, CSS, `_data` YAML을 저장하면 브라우저가 자동으로 새로고침됩니다. 서버를 끄려면 해당 터미널에서 `Ctrl + C`를 누릅니다.

> `index.html`을 탐색기에서 더블클릭해 열면 CSS와 경로가 깨집니다. 반드시 위 주소로 접속하세요.

### 자주 쓰는 명령

| 명령 | 설명 |
| --- | --- |
| `bundle exec jekyll serve` | 로컬 서버 (포트 4000) |
| `bundle exec jekyll serve --livereload` | 저장 시 브라우저 자동 새로고침 |
| `bundle exec jekyll serve --port 4001` | 4000번 포트가 사용 중일 때 |
| `bundle exec jekyll build` | `_site` 폴더로 정적 파일만 생성 |

### 문제가 생길 때

**`jekyll`을 찾을 수 없음 / webrick 오류**  
전역 `jekyll serve`가 아니라 반드시 `bundle exec jekyll serve`를 사용하세요. `Gemfile`의 버전으로 실행됩니다.

**`bundle install` 중 native extension 오류 (Windows)**  
RubyInstaller Devkit/MSYS2가 빠진 경우가 많습니다. `ridk install`을 다시 실행한 뒤 `bundle install`을 재시도하세요.

**타임존 오류 (`TZInfo::DataSourceNotFound`)**  
Windows에서 자주 납니다. 이 저장소 `Gemfile`에 `tzinfo-data`가 들어 있으므로 `bundle install` 후 다시 실행하세요.

**포트 4000이 이미 사용 중**

```powershell
bundle exec jekyll serve --port 4001
```

**페이지 스타일이 안 보임**  
주소가 `http://127.0.0.1:4000`인지 확인하세요. 빌드 결과물(`_site`)을 파일로 직접 열면 루트 경로(`/assets/...`)가 맞지 않습니다.

## 콘텐츠 수정

대부분의 문구는 코드 대신 아래 파일만 고치면 됩니다.

| 파일 | 역할 |
| --- | --- |
| `_config.yml` | 사이트 제목, 소개, GitHub/LinkedIn, 이메일 |
| `_data/nav.yml` | 상단 메뉴 |
| `_data/skills.yml` | 소개 영역의 역량 카드 |
| `_data/experience.yml` | 경험 |
| `_data/projects.yml` | 프로젝트 목록 |
| `_includes/` | 히어로, 소개, 경험 등 섹션 마크업 |
| `_sass/` | 색, 타이포, 레이아웃 |

이메일을 버튼으로 노출하려면 `_config.yml`의 `email`에 주소를 넣으세요.

## GitHub Pages에 올리기

이 사이트는 Jekyll 4를 쓰므로 **GitHub Actions**로 배포합니다. `.github/workflows/pages.yml`이 포함되어 있습니다.

1. 코드를 `main` 브랜치에 푸시합니다.
2. GitHub 저장소 **Settings → Pages**
3. **Build and deployment → Source**를 **GitHub Actions**로 선택합니다.
4. Actions 탭에서 `Deploy Jekyll site to Pages` 워크플로가 초록색인지 확인합니다.

수 분 뒤 `https://inyounglee.github.io`에서 확인할 수 있습니다.

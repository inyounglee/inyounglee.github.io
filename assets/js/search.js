(function () {
  var form = document.getElementById("search-form");
  var input = document.getElementById("search-input");
  var grid = document.getElementById("search-grid");
  var empty = document.getElementById("search-empty");
  var hint = document.getElementById("search-hint");
  var resultsWrap = document.getElementById("search-results");
  var postGrid = document.getElementById("post-grid");
  var listSection = document.getElementById("list");
  var featuredSection = document.querySelector(".featured-section");

  if (!input || !grid) return;

  var topicFilter = (input.getAttribute("data-topic") || "").trim();
  var cache = null;
  var searchIndexUrl = (document.body.getAttribute("data-baseurl") || "") + "/search.json";

  // baseurl from first stylesheet as fallback
  var cssLink = document.querySelector('link[href*="main.css"]');
  if (cssLink) {
    searchIndexUrl = cssLink.href.replace(/assets\/css\/main\.css.*$/, "search.json");
  }

  function cardHtml(item) {
    var image = item.image
      ? '<img src="' + item.image + '" alt="" loading="lazy">'
      : '<div class="media-fallback" aria-hidden="true"></div>';
    return (
      '<a class="post-card" href="' +
      item.url +
      '">' +
      '<div class="post-card-media">' +
      image +
      "</div>" +
      '<div class="post-card-body">' +
      "<h3>" +
      escapeHtml(item.title) +
      "</h3>" +
      '<p class="post-card-date">' +
      escapeHtml(item.date || "") +
      "</p>" +
      "</div></a>"
    );
  }

  function escapeHtml(str) {
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function normalize(text) {
    return String(text || "").toLowerCase();
  }

  function filterPosts(posts, query) {
    var q = normalize(query);
    return posts.filter(function (post) {
      if (topicFilter && !(post.categories || []).includes(topicFilter)) {
        return false;
      }
      if (!q) return false;
      var hay = [post.title, post.excerpt, post.content, (post.categories || []).join(" ")].join(" ");
      return normalize(hay).indexOf(q) !== -1;
    });
  }

  function render(items, query) {
    var hasQuery = Boolean(query && query.trim());
    if (resultsWrap) resultsWrap.hidden = !hasQuery;
    if (listSection) listSection.hidden = hasQuery;
    if (featuredSection) featuredSection.hidden = hasQuery;
    if (postGrid && !resultsWrap) {
      // search page: keep grid only
    }

    if (hint) hint.hidden = hasQuery;

    if (!hasQuery) {
      grid.innerHTML = "";
      if (empty) empty.hidden = true;
      return;
    }

    grid.innerHTML = items.map(cardHtml).join("");
    if (empty) empty.hidden = items.length > 0;
  }

  function loadIndex() {
    if (cache) return Promise.resolve(cache);
    return fetch(searchIndexUrl)
      .then(function (res) {
        if (!res.ok) throw new Error("search index missing");
        return res.json();
      })
      .then(function (data) {
        cache = data;
        return cache;
      });
  }

  function runSearch(query) {
    loadIndex()
      .then(function (posts) {
        render(filterPosts(posts, query), query);
      })
      .catch(function () {
        grid.innerHTML = "";
        if (empty) {
          empty.hidden = false;
          empty.textContent = "검색 인덱스를 불러오지 못했습니다.";
        }
      });
  }

  if (form) {
    form.addEventListener("submit", function (e) {
      // topic pages: inline filter; dedicated search page uses GET
      if (resultsWrap || topicFilter) {
        e.preventDefault();
        runSearch(input.value);
        var url = new URL(window.location.href);
        if (input.value.trim()) url.searchParams.set("q", input.value.trim());
        else url.searchParams.delete("q");
        history.replaceState(null, "", url);
      }
    });
  }

  var debounce;
  input.addEventListener("input", function () {
    clearTimeout(debounce);
    debounce = setTimeout(function () {
      if (resultsWrap || document.body.classList.contains("search-live") || topicFilter) {
        runSearch(input.value);
      }
    }, 180);
  });

  var params = new URLSearchParams(window.location.search);
  var initial = params.get("q");
  if (initial) {
    input.value = initial;
    runSearch(initial);
  }
})();

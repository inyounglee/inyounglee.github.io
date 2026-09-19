# frozen_string_literal: true

# 포스트 HTML에서 검은사막 아이템명을 찾아 제작 계산기 링크를 건다.
# 아이템 목록: _data/bdo_craft_items.json (auto/script/build-bdo-item-links.py)

require "erb"

module BdoCraftItemLinks
  BASE = "https://bdo-craft-calc.inyounglee.kr/kr/items"
  SKIP_TAGS = %w[a code pre kbd script style textarea svg button].freeze
  TOKEN = /(<[^>]+>|[^<]+)/

  module_function

  def item_slug(name)
    name.to_s.strip.gsub(%r{[\\/#?]+}, "").gsub(/\s+/, "-")
  end

  def item_href(name, base = BASE)
    slug = item_slug(name)
    encoded = ERB::Util.url_encode(slug).gsub("%2D", "-")
    "#{base}/#{encoded}"
  end

  def apply(html, names, base = BASE)
    return html if html.nil? || html.empty? || names.nil? || names.empty?

    pattern = names.map { |n| Regexp.escape(n) }.join("|")
    # 왼쪽은 단어 경계. 오른쪽은 조사만 허용해 '자라기를' 같은 오탐을 막는다.
    particle = "은|는|이|가|을|를|의|에|와|과|도|로|만|며|고|나|든|랑|께|까지|부터|처럼|보다|으로|에서|에게|한테"
    item_re = /(?<!\p{Alnum})(?:#{pattern})(?=(?:#{particle})?(?:[^\p{Alnum}]|\z))/

    skip_depth = 0
    html.gsub(TOKEN) do |token|
      if token.start_with?("<")
        skip_depth = update_skip_depth(token, skip_depth)
        token
      elsif skip_depth.positive?
        token
      else
        token.gsub(item_re) do |match|
          href = item_href(match, base)
          %(<a class="craft-item" href="#{href}" target="_blank" rel="noopener noreferrer" title="제작 계산기에서 보기">#{match}</a>)
        end
      end
    end
  end

  def update_skip_depth(tag, depth)
    return depth if tag.start_with?("<!") || tag.start_with?("<?")
    return depth if tag.end_with?("/>")

    m = tag.match(/\A<\/?\s*([A-Za-z][\w:-]*)/)
    return depth unless m

    name = m[1].downcase
    return depth unless SKIP_TAGS.include?(name)

    if tag.start_with?("</")
      [depth - 1, 0].max
    else
      depth + 1
    end
  end
end

Jekyll::Hooks.register :posts, :post_convert do |post|
  names = post.site.data["bdo_craft_items"]
  next unless names.is_a?(Array) && !names.empty?

  base = post.site.config.dig("bdo_craft_calc", "item_base") || BdoCraftItemLinks::BASE
  post.content = BdoCraftItemLinks.apply(post.content, names, base)
end

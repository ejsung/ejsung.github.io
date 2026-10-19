---
title: "Tags"
layout: archive
permalink: /tags/
author_profile: true
---

{% comment %}
Minimal Mistakes links page tags to /tags/#slug, but site.tags only indexes
posts. This archive also indexes the tags attached to academic pages.
{% endcomment %}
{% assign all_tag_names = "" %}
{% for entry in site.pages %}
  {% for tag in entry.tags %}
    {% assign all_tag_names = all_tag_names | append: tag | append: "|" %}
  {% endfor %}
{% endfor %}
{% assign tag_names = all_tag_names | split: "|" | uniq | sort_natural %}

{% for tag in tag_names %}
  {% if tag != "" %}
<h2 id="{{ tag | slugify }}">{{ tag | escape }}</h2>
<ul>
  {% for entry in site.pages %}
    {% if entry.tags contains tag %}
  <li><a href="{{ entry.url | relative_url }}">{{ entry.title | escape }}</a></li>
    {% endif %}
  {% endfor %}
</ul>
  {% endif %}
{% endfor %}

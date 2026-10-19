---
title: "Research"
layout: single
date: 2021-12-02
classes: wide
permalink: /research/
tags: [research, math, physics, publication, preprint, poster, conference]
---
**Note**: I primarily publish under Eric J. Sung. However, some of my (earlier) works are published under Junhyup Sung. 

### Research Interests 
Condensed Matter Physics, Nonequilibrium Quantum Many-Body Physics, Scientific Machine Learning, General Relativity

### Publications

{% bibliography --query @article %}

### Under Review

{% bibliography --query @misc %}

### Conference Presentations and Abstracts

{% bibliography --query @inproceedings %}

### Conferences and Workshops Attended

<ul>
{% for conference in site.data.conferences %}
  <li>
    {{ conference.name | escape }}{% if conference.presentation %} (<strong>{{ conference.presentation | escape }}</strong>){% endif %}, {{ conference.date | escape }}. {{ conference.location | escape }}.
  </li>
{% endfor %}
</ul>

### Master's Thesis
<a href = "https://www.proquest.com/docview/2561419290/abstract/5A2A42E7A9224893PQ/1" target="_blank">*Mathematics and Applications of Feynman Diagrams*</a>  
Thesis Advisor: <a href = "https://sse.tulane.edu/victor-h-moll" target = "_blank">Prof. Victor H. Moll</a> 

### Undergraduate Senior Seminar Paper
*Mathematical Fluid Dynamics of Microorganisms*  
Seminar Advisor: <a href = "https://sse.tulane.edu/lisa-j-fauci" target = "_blank">Prof. Lisa J. Fauci</a> 
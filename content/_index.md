---
# Leave the homepage title empty to use the site title
title: ''
summary: ''
date: 2026-08-14
type: landing

sections:
  - block: hero
    content:
      eyebrow: 'School of Mechanical Engineering, NTUA'
      title: 'Laboratory of [Biofluid Mechanics] & Biomedical Technology'
      text: |-
        Placeholder mission statement — replace with a real description of the lab's research mission and focus areas.
      primary_action:
        text: Explore Research Areas
        url: /research/research-areas/
      secondary_action:
        text: Meet the Team
        url: /people/
    design:
      layout: centered
      alignment: center

  - block: research-areas
    content:
      title: Research Areas
      text: A quick look at what we work on — see the full [Research Areas](/research/research-areas/) page for details.
      items:
        - name: Cardiovascular & Hemodynamics
          description: Flow in arteries, heart valves, and stents.
          emoji: 🫀
          gradient: from-red-400 to-pink-500
        - name: Microfluidics & Lab-on-a-Chip
          description: Miniaturized flow platforms for diagnostics.
          emoji: 🔬
          gradient: from-cyan-400 to-blue-500
        - name: Biomedical Device Design & Testing
          description: Design and in vitro testing of medical devices.
          emoji: ⚙️
          gradient: from-teal-400 to-emerald-500
        - name: Flow Imaging & Diagnostics
          description: Experimental and computational flow measurement.
          emoji: 🌊
          gradient: from-indigo-400 to-purple-500
    design:
      layout: cards

  - block: collection
    id: publications
    content:
      title: Featured Publications
      filters:
        tags:
          - Publication
        featured_only: true
    design:
      view: article-grid
      columns: 2

  - block: team-showcase
    content:
      title: Principal Investigator
      user_groups:
        - Principal Investigators
      cta:
        text: Meet the Full Team
        url: /people/
    design:
      show_role: true
      show_organizations: false
      show_interests: false
      max_columns: 4

  - block: collection
    id: news
    content:
      title: Recent News
      filters:
        folders:
          - news
      count: 3
    design:
      view: card

  - block: cta-card
    content:
      title: Interested in joining the lab?
      text: |-
        We welcome motivated students for diploma and MSc theses. See our currently available thesis topics, or get in touch.
      button:
        text: View Open Theses Subjects
        url: /theses/open-theses-subjects/
    design:
      card:
        css_class: 'bg-primary-300 dark:bg-primary-700'
---

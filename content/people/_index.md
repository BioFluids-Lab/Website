---
title: People
type: landing

sections:
  - block: bf-phead
    content:
      eyebrow: Laboratory
      title: People
      text: >-
        The laboratory is a small group. Most of the measuring is done by doctoral
        and diploma students, supervised across the four research areas.

  - block: team-showcase
    content:
      user_groups:
        # Sorted by the `weight` in each data/authors/*.yaml, not by surname,
        # so Christos Manopoulos leads regardless of who is added later.
        - name: Professors
          sort_by: weight
        - name: Staff
          sort_by: weight
        - name: PhD Students
          sort_by: weight
        - MSc / Undergraduate Students
        - name: Alumni
          sort_by: graduation_year
          sort_ascending: false
      cta:
        text: Theses subjects
        url: /theses-subjects/
    design:
      show_role: true
      show_organizations: false
      show_interests: false
      max_interests: 3
      align: center
      max_columns: 4
      show_social: true
      show_empty_groups: false
---

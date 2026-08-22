---
title: ""
summary: ""
date: 2026-08-22
type: landing

sections:
  - block: bf-hero
    content:
      title: 'We measure how <span class="bf-em">fluids move</span> <span class="bf-thin">through the human body.</span>'
      text: >-
        The Laboratory of Biofluid Mechanics &amp; Biomedical Technology studies
        cardiovascular flow, microfluidic transport, and the devices built to work
        inside them. We combine in vitro flow rigs, particle image velocimetry, and
        computational modelling to turn measurement into design.
      primary_action:
        text: Research areas
        url: /research/research-areas/
      secondary_action:
        text: Theses subjects
        url: /theses-subjects/
      plate:
        tag: Live
        scale: 10 mm
        mode: vortex
        seed: 5
        animate: true
        alt: Particle flow field downstream of a mechanical heart valve
        caption: >-
          Particle tracking downstream of a bileaflet mechanical valve. Re = 4500,
          peak systole. Colour encodes velocity magnitude.

  - block: bf-readout
    content:
      items:
        - value: "1994"
          label: Established
        - value: "38"
          label: Publications
        - value: "6"
          label: Ongoing projects
        - value: "5"
          label: Active PhDs

  - block: bf-cards
    content:
      title: Four questions the lab keeps returning to.
      text: >-
        Each area runs its own rigs and its own students, but they share the same
        instruments and the same underlying problem: how a fluid behaves when the
        boundary is soft, pulsatile, and alive.
      items:
        - name: Cardiovascular & Hemodynamics
          description: Pulsatile flow in arteries, heart valves and stents, measured in compliant in vitro models.
          url: /research/research-areas/
          mode: vortex
          seed: 3
          topics: [Heart valves, Stenosis, Wall shear]
        - name: Microfluidics & Lab-on-a-Chip
          description: Miniaturised platforms for cell sorting, blood analogue rheology, and point-of-care diagnostics.
          url: /research/research-areas/
          mode: channel
          seed: 11
          topics: [Cell sorting, Droplets, Rheology]
        - name: Biomedical Device Design
          description: Design, prototyping and in vitro qualification of implants and extracorporeal circuits.
          url: /research/research-areas/
          mode: wake
          seed: 27
          topics: [Prototyping, Hemolysis, ISO 5840]
        - name: Flow Imaging & Diagnostics
          description: Method development for PIV, PTV and image-based velocimetry in optically difficult geometries.
          url: /research/research-areas/
          mode: shear
          seed: 41
          topics: [PIV / PTV, Tomographic, Uncertainty]

  - block: bf-bib
    content:
      title: Recent publications
      text: A running record of what the lab has measured, modelled and put into print.
      count: 3
      cta:
        text: All publications
        url: /research/publications/
    design:
      tint: true

  - block: team-showcase
    content:
      title: The people running the rigs
      subtitle: ""
      text: >-
        One principal investigator, a postdoctoral cohort, and the doctoral and
        diploma students who do most of the measuring.
      user_groups:
        - Principal Investigators
        - Postdoctoral Researchers
      cta:
        text: Meet the full team
        url: /people/
    design:
      show_role: true
      show_organizations: false
      show_interests: false
      max_columns: 4

  - block: bf-rows
    content:
      title: Lab notes
      items:
        - date: 12 Jun 2026
          title: New pulsatile flow loop commissioned in the hemodynamics rig
          category: Facilities
          url: /news/
        - date: 28 May 2026
          title: Paper accepted at the European Conference on Biofluid Mechanics
          category: Publication
          url: /news/
        - date: 09 Apr 2026
          title: Three diploma theses defended on microfluidic cell separation
          category: Theses
          url: /news/
      cta:
        text: All news
        url: /news/
    design:
      tint: true

  - block: bf-cta
    content:
      title: Looking for a thesis topic?
      text: >-
        We take diploma and MSc students every semester. Topics are posted with the
        rig you would work on and the skills you would leave with.
      mode: shear
      seed: 19
      actions:
        - text: Theses subjects
          url: /theses-subjects/
        - text: Contact the lab
          url: /contact/
          ghost: true
---

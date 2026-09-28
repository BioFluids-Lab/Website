---
title: Self-supervised pre-training with intensity guided masking for enhanced aorta
  segmentation in CT
authors:
- T.P. Vagenas
- I. Vezakis
- I. Kakkos
- C. Mavridis
- T. Economopoulos
- A. Anastasiou
- Anastasios Raptis
- Christos Manopoulos
- G.K. Matsopoulos
date: '2025-01-01'
publishDate: '2026-08-30T08:44:55.838120Z'
publication_types:
- paper-conference
publication: '*Proc. Annu. Int. Conf. IEEE Eng. Med. Biol. Soc. EMBS*'
hugoblox:
  ids:
    doi: 10.1109/EMBC58623.2025.11253827
abstract: Abdominal aortic aneurysm (AAA) is a life-threatening vascular condition
  that requires regular imaging and follow-ups to prevent fatal outcomes. While accurate
  diagnosis and selecting treatment strategies depend on aortic segmentation to assess
  disease progression, manual segmentation is time-consuming, prone to inter-observer
  variability, and can stall the clinical workflow. For the automatic aorta segmentation
  several deep learning methods have been proposed with high accuracy. However, their
  reliance on large annotated databases limits their applicability. To this end, self-supervised
  learning approaches have been developed to alleviate the need for manual labels
  during training. In CT imaging, Hounsfield Units (HU) correspond to specific anatomical
  structures, such as bones and soft tissues, based on their intensity ranges. In
  this paper, we exploit this property to effectively pre-train a Deep Learning segmentation
  model using the proposed Intensity Guided Masking (IGM) where we occlude regions
  within specific intensity ranges in the CT image and aim at predicting/reconstructing
  the masked area. Next, the pre-trained encoder is integrated into a SwinUNETR model,
  fine-tuned on manually labeled CT images, and evaluated for aortic structure segmentation.
  Our proposed method has been evaluated on both a public and a private dataset achieving
  DSC of 91.20% and 85% and ASSD of 0.05mm and 0.04mm, respectively and outperforming
  both state-of-the-art supervised baselines and pre-training based methods. The code
  will be released upon publication at https://github.com/theoVag/SwinUNETR-IGM.Clinical
  relevance - Our method improves aortic segmentation accuracy in CT imaging while
  reducing reliance on large annotated datasets, enhancing efficiency in vascular
  condition assessment such as detecting or quantifying abdominal aortic aneurysms.  ©
  2025 IEEE.
links:
- name: URL
  url: https://doi.org/10.1109/EMBC58623.2025.11253827
---

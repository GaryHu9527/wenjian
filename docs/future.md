# Future enhancements

## GuwenBERT

GuwenBERT (<https://github.com/Ethan-yt/guwenbert>) was reviewed but is intentionally not installed for the competition build. A future deployment can evaluate it for sentence segmentation, named-entity recognition and contextual representations after model-serving capacity, evaluation data and a compatible runtime are available.

## Poetry API adapter

The `PoetryProvider` contract is ready for an adapter to palemoky/chinese-poetry-api. Its REST search endpoint is `/api/v1/poems/search?q=...`; no Go service is bundled or deployed by this project.

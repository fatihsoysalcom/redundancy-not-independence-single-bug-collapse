# Redundancy Not Independence Single Bug Collapse

This example demonstrates how a single software bug in a shared critical component can lead to a complete system collapse, even in a highly redundant setup with multiple instances across different data centers. It simulates a scenario where all service instances depend on the same shared component. When a specific 'poison pill' input triggers a bug in this shared component, it enters a failed state, causing all dependent service instances to become unhealthy, illustrating that redundancy does not always guarantee independence.

## Language

`python`

## How to Run

Save the code as `main.py`.
Run from your terminal: `python main.py`

## Original Article

This example accompanies the Turkish article: [Redundans Bağımsızlık Değilse Ne Olur? Tek Hata, Büyük Çöküş](https://fatihsoysal.com/blog/redundans-bagimsizlik-degilse-ne-olur-tek-hata-buyuk-cokus/).

## License

MIT — see [LICENSE](LICENSE).

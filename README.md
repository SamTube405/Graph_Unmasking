
# Graph_Unmasking

Python codebase to mount meachine-learning based de-anonymization attacks on social graphs, and explaining the success of such attack via network metrics

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
* snap
* pandas
* numpy
* itertools
* matplotlib
* sklearn
* imblearn
```

### Installing

A step by step series of examples that tell you how to get a development env running


```
cd scripts/
./run_attack_model.sh fb107 fb107
```

And repeat

```
./run_attack_model.sh caGrQc caGrQc
./run_attack_model.sh soc-anybeat soc-anybeat
./run_attack_model.sh soc-gplus soc-gplus
./run_attack_model.sh <graph name> <synthetic graph name>
```


## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [snap](https://snap.stanford.edu)
* [sklearn](https://snap.stanford.edu) 

## Contributing

Please read [CONTRIBUTING.md]() for details on our code of conduct, and the process for submitting pull requests to us.


## Authors

* **Sameera Horawalavithana** - *Initial work*

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc


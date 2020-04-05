# YALSE

**Y**et **A**nother **L**ocal **S**earch **E**ngine

As a [/r/datahoarder](https://www.reddit.com/r/DataHoarder/) I have the need to 
* index all the documents in my [unRAID](https://unraid.net/) server
* spot duplicates based on actual content
* full-text search items and metadata

After trying other tools, I decided to go with *yet another* solution.

**[DISCLAIMER]**: This project is a work in progress

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites


```
[WIP]
```

### Installing


```
sysctl -w vm.max_map_count=262144
docker-compose up --scale yalse-worker=2
```


## Deployment

```
[WIP]
```

## Built With

* [Connexion](https://github.com/zalando/connexion) - API First backend framework (Flask-based)
* [Elasticsearch](https://www.elastic.co/) - Search engine
* [RQ](https://python-rq.org/) - Library for queueing jobs
* [Tika](https://tika.apache.org/) - File content and metadata extractor

## Versioning

I use [SemVer](http://semver.org/) for versioning. 

0.1.2 Pre-Alpha
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

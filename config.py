# import watchtower, logging
from boto3.session import Session

accessKey = "AKIAIOLCWJR3G7IUJ3MQ"
accessSecret = "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"
region = "us-east-1"
boto3_session = Session(aws_access_key_id=accessKey,
                        aws_secret_access_key=accessSecret,
                        region_name=region)
connect = {
   "redis":{
        "host":"34.83.74.41",
        "password":"HJ65kE8XmAST",
        "port":6379,
        "db":0
    },
    "rmq":{
        "host":'amqp://user:qrp5KTzg6Bdo@34.83.40.87:5672/%2F'
    },
    "aws":{
        "accessKey":"AKIAIOLCWJR3G7IUJ3MQ",
        "accessSecret":"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",
        "region":"us-east-1"
    },
    "postgress":{
        "host":"postgresql://eunimart_user:o2R7chzDlxEYKDvp2g2W@crawl-data.cluster-cqxnvh2hudf5.us-east-2.rds.amazonaws.com:5432/crawled_data"
    },
    "mysql":{
        "host":"mysql+pymysql://root:root@127.0.0.1:3306/schedular_data"
    },
    "s3_bucket":{
        "bucket":"new-crawling-data"
    },
    "logger_config":  {
                    "version": 1,
                    "disable_existing_loggers": False,
                    "formatters": {
                        "simple": {
                            "format": "%(message)s"
                        },
                        "extended": {
                            "format": "(%(thread)d)%(asctime)s : [%(levelname)s] : %(module)s:%(lineno)d | %(message)s"
                        },
                        "json": {
                            "format": "name: %(name)s, level: %(levelname)s, time: %(asctime)s, message: %(message)s"
                            }
                    },

                    "handlers": {
                        "console": {
                            "class": "logging.StreamHandler",
                            "level": "CRAWL_DEBUG",
                            "formatter": "extended",
                            "stream": "ext://sys.stdout"
                        },
                        "crawl_file_handler": {
                            'level': 'CRAWL_DEBUG',
                            'class': 'watchtower.CloudWatchLogHandler',
                            'boto3_session': boto3_session,
                            'log_group': 'crawler_logs_v1.4',
                            'stream_name': 'crawl_debug',
                            'formatter': 'extended',
                        },

                        "info_file_handler": {
                            'level': 'INFO',
                            'class': 'watchtower.CloudWatchLogHandler',
                            'boto3_session': boto3_session,
                            'log_group': 'crawler_logs_v1.4',
                            'stream_name': 'info',
                            'formatter': 'extended',
                        },
                        "debug_file_handler": {
                            'level': 'DEBUG',
                            'class': 'watchtower.CloudWatchLogHandler',
                            'boto3_session': boto3_session,
                            'log_group': 'crawler_logs_v1.4',
                            'stream_name': 'debug',
                            'formatter': 'extended',
                        },
                        

                        "error_file_handler": {
                            'level': 'ERROR',
                            'class': 'watchtower.CloudWatchLogHandler',
                            'boto3_session': boto3_session,
                            'log_group': 'crawler_logs_v1.4',
                            'stream_name': 'error',
                            'formatter': 'extended',
                        }
                        
                    },

                    "loggers": {
                        # Fine-grained logging configuration for individual modules or classes
                        # Use this to set different log levels without changing 'real' code.
                    },

                    "root": {
                        # Set the level here to be the default minimum level of log record to be produced
                        # If you set a handler to level DEBUG you will need to set either this level, or
                        # the level of one of the loggers above to DEBUG or you won't see any DEBUG messages
                        "level": "CRAWL_DEBUG",
                        "handlers": ["error_file_handler", "debug_file_handler", "console"]
                    }
    }

}

_connect = {
   "redis":{
        "host":"34.83.74.41",
        "password":"HJ65kE8XmAST",
        "port":6379,
        "db":0
    },
    "rmq":{
        "host":'amqp://ravi:ravi1234@127.0.0.1:5672/%2F'
    },
    "aws": {
            "accessKey": "AKIAIOLCWJR3G7IUJ3MQ",
            "accessSecret": "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",
            "region": "ap-south-1"
    },
    "s3_bucket":{
            "bucket":"crawling-testing"
    },
    "postgress":{
        "host":"postgresql://ravi:testing@127.0.0.1:5432/testing"
    },
    "mysql":{
        "host":"mysql+pymysql://root:root@127.0.0.1:3306/schedular_data"
    },
    "logger_config":  {
                    "version": 1,
                    "disable_existing_loggers": False,
                    "formatters": {
                        "simple": {
                            "format": "%(message)s"
                        },
                        "extended": {
                            "format": "(%(thread)d)%(asctime)s : [%(levelname)s] : %(module)s:%(lineno)d | %(message)s"
                        },
                        "json": {
                            "format": "name: %(name)s, level: %(levelname)s, time: %(asctime)s, message: %(message)s"
                            }
                    },

                    "handlers": {
                        "console": {
                            "class": "logging.StreamHandler",
                            "level": "CRAWL_DEBUG",
                            "formatter": "extended",
                            "stream": "ext://sys.stdout"
                        },
                        
                        
                    },

                    "loggers": {
                        # Fine-grained logging configuration for individual modules or classes
                        # Use this to set different log levels without changing 'real' code.
                    },

                    "root": {
                        # Set the level here to be the default minimum level of log record to be produced
                        # If you set a handler to level DEBUG you will need to set either this level, or
                        # the level of one of the loggers above to DEBUG or you won't see any DEBUG messages
                        "level": "ERROR",
                        "handlers": ["console"]
                    }
    }

}

connect_local = {
    "redis":{
        "host":"127.0.0.1",
        "port":6379,
        "db":0
    },
    "rmq":{
        "host":'amqp://test:test@127.0.0.1:5672/%2F'
    },
    "aws": {
            "accessKey": "AKIAIOLCWJR3G7IUJ3MQ",
            "accessSecret": "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",
            "region": "ap-south-1"
    },
    "s3_bucket":{
            "bucket":"eunimart-crawling-testing"
    }
}

connect_prod = {
    "redis":{
        "host":"35.193.110.33",
        "password":"JsoCTpSyt8jN",
        "port":6379,
        "db":0
    },
    "rmq":{
        "host":'amqp://crawler_worker:ZgHELCX1yoAT@35.232.24.59:5672/%2F'
    },
    "aws": {
            "accessKey": "AKIAIOLCWJR3G7IUJ3MQ",
            "accessSecret": "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",
            "region": "ap-south-1"
    },
    "s3_bucket":{
                "bucket":"eunimart-crawlers-data"
    }
}
#!/bin/sh
mkdir -p /var/log/gunicorn
gunicorn app:app
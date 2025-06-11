.PHONY: up down build clean test dev install

up:
	docker-compose up -d

down:
	docker-compose down

build:
	docker-compose build

clean:
	docker-compose down -v
	Remove-Item -Recurse -Force -ErrorAction SilentlyContinue volumes/generated_sites/*
	Remove-Item -Recurse -Force -ErrorAction SilentlyContinue volumes/user_uploads/*
	Get-ChildItem -Path volumes/generated_sites,.gitkeep -Force | Move-Item -Destination volumes/generated_sites
	Get-ChildItem -Path volumes/user_uploads,.gitkeep -Force | Move-Item -Destination volumes/user_uploads

dev:
	docker-compose up --build

install:
	python -m venv venv
	.\venv\Scripts\Activate.ps1
	pip install -r ai-hugo-frontend/requirements.txt
	pip install -r ai-hugo-backend/requirements.txt

test:
	.\venv\Scripts\Activate.ps1
	python -m pytest

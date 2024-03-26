ARTIFACTS = dz?_task?_images dz?/task?_doc

all:
	python3 main.py

clean:
	rm -fr $(ARTIFACTS)

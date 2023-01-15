batch() {
	for arg; do
		node index.js &
	done
	wait
}

for i in {1..100}; do echo $i; batch {1..5}; done

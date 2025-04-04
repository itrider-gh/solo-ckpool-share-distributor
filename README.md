# solo-ckpool-share-distributor
A Python utility for computing and distributing mining rewards across individual workers on a ckpool instance running in solo mode (-B). It parses .sharelog files and calculates each worker’s contribution based on share count and average vardiff, assuming all miners are mining to the same solo_username address.

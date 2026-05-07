# catalog-progressive-load

Make card catalog loading feel instant: eagerly initialize the fireplace DB and pre-build the catalog at server startup (taking the multi-second XML parse off the request hot path), persist the built catalog to disk as a sidecar cache so server restarts skip the parse, and stream/page the payload to the client so the browse UI renders the filter rail and first page immediately rather than blocking on a 1.8 MB JSON download.

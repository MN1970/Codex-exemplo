module github.com/mantaassociados/manta-otel

go 1.21

require (
	go.opentelemetry.io/otel v1.21.0
	go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc v1.21.0
	go.opentelemetry.io/otel/exporters/prometheus v0.45.0
	go.opentelemetry.io/otel/sdk v1.21.0
	go.opentelemetry.io/otel/sdk/metric v1.21.0
	go.opentelemetry.io/otel/trace v1.21.0
	go.opentelemetry.io/otel/instrumentation/net/http v0.45.0
	go.opentelemetry.io/otel/instrumentation/database/sql v0.45.0
	github.com/prometheus/client_golang v1.18.0
	google.golang.org/grpc v1.60.0
)

require (
	github.com/cenkalti/backoff/v4 v4.2.1 // indirect
	github.com/grpc-ecosystem/grpc-gateway/v2 v2.18.0 // indirect
	github.com/prometheus/client_model v0.5.0 // indirect
	github.com/prometheus/common v0.45.0 // indirect
	github.com/prometheus/procfs v0.12.0 // indirect
	golang.org/x/net v0.20.0 // indirect
	golang.org/x/sys v0.16.0 // indirect
	golang.org/x/text v0.13.0 // indirect
	google.golang.org/genproto/googleapis/api v0.0.0-20231211222908-948df8e49b3d // indirect
	google.golang.org/genproto/googleapis/rpc v0.0.0-20231212172506-995d672761c0 // indirect
	google.golang.org/protobuf v1.32.0 // indirect
)

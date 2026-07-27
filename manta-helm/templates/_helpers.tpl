{{/*
Expand the name of the chart.
*/}}
{{- define "manta.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "manta.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "manta.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "manta.labels" -}}
helm.sh/chart: {{ include "manta.chart" . }}
{{ include "manta.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- with .Values.commonLabels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "manta.selectorLabels" -}}
app.kubernetes.io/name: {{ include "manta.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "manta.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "manta.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Determine image pull policy
*/}}
{{- define "manta.imagePullPolicy" -}}
{{- .Values.imagePullPolicy | default "IfNotPresent" }}
{{- end }}

{{/*
Return the appropriate apiVersion for Deployment
*/}}
{{- define "manta.deploymentApiVersion" -}}
{{- if .Capabilities.APIVersions.Has "apps/v1" }}
apps/v1
{{- else }}
apps/v1beta1
{{- end }}
{{- end }}

{{/*
Return the appropriate apiVersion for StatefulSet
*/}}
{{- define "manta.statefulsetApiVersion" -}}
{{- if .Capabilities.APIVersions.Has "apps/v1" }}
apps/v1
{{- else }}
apps/v1beta1
{{- end }}
{{- end }}

{{/*
Return the appropriate apiVersion for HorizontalPodAutoscaler
*/}}
{{- define "manta.hpaApiVersion" -}}
{{- if .Capabilities.APIVersions.Has "autoscaling/v2" }}
autoscaling/v2
{{- else if .Capabilities.APIVersions.Has "autoscaling/v2beta2" }}
autoscaling/v2beta2
{{- else }}
autoscaling/v1
{{- end }}
{{- end }}

{{/*
Return the appropriate apiVersion for NetworkPolicy
*/}}
{{- define "manta.networkPolicyApiVersion" -}}
{{- if .Capabilities.APIVersions.Has "networking.k8s.io/v1" }}
networking.k8s.io/v1
{{- else }}
networking.k8s.io/v1beta1
{{- end }}
{{- end }}

{{/*
Return the appropriate apiVersion for PodSecurityPolicy
*/}}
{{- define "manta.podSecurityPolicyApiVersion" -}}
{{- if .Capabilities.APIVersions.Has "policy/v1" }}
policy/v1
{{- else }}
policy/v1beta1
{{- end }}
{{- end }}

{{/*
Return the PostgreSQL client connection string
*/}}
{{- define "manta.postgresqlConnection" -}}
postgresql://{{ .Values.postgres.auth.username }}@{{ include "manta.fullname" . }}-postgres-client.{{ .Values.namespace }}.svc.cluster.local:{{ .Values.postgres.service.port }}/{{ .Values.postgres.auth.database }}
{{- end }}

{{/*
Return the FastAPI internal URL
*/}}
{{- define "manta.fastAPIUrl" -}}
http://{{ include "manta.fullname" . }}-fastapi-internal.{{ .Values.namespace }}.svc.cluster.local:{{ .Values.fastapi.service.port }}
{{- end }}

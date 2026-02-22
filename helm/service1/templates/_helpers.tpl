{{/*
Common labels
*/}}
{{- define "service1.labels" -}}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{ include "service1.selectorLabels" . }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels — used by both the Deployment selector and NetworkPolicy
*/}}
{{- define "service1.selectorLabels" -}}
app: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

---
name: kubernetes-manifest-generator
description: "Generates Kubernetes manifests including deployments, services, and ingress from application analysis. Use when containerizing for K8s, creating deployment configs, or migrating to Kubernetes. Also applies when: 'generate K8s manifests', 'create deployment yaml', 'Kubernetes setup', 'helm chart scaffold'."
---

# Kubernetes Manifest Generator

This skill generates production-grade Kubernetes manifests by analyzing the application's runtime requirements, dependencies, and configuration. It produces Deployment, Service, Ingress, ConfigMap, Secret, and HorizontalPodAutoscaler manifests with appropriate resource limits, health checks, and security contexts.

## Prerequisites

Confirm the target application directory with the user. Determine whether the output should be plain Kubernetes YAML or a Helm chart scaffold. Identify the target cluster environment (development, staging, production) as this affects resource sizing and replica counts.

## Step 1: Analyze Application Requirements

Use `filesystem` to scan the project structure and `data_file_read` to examine configuration files.

Identify the following:

1. **Runtime and language**: Detect from `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`, or `Dockerfile`.
2. **Existing Dockerfile**: If a Dockerfile exists, parse it to determine:
   - Base image and version.
   - Exposed ports.
   - Entry point and command.
   - Build stages (multi-stage builds).
   - Environment variables referenced.
3. **Application ports**: Check for port configuration in:
   - Source code: listen calls, bind addresses, server configuration.
   - Configuration files: `.env`, `config.yaml`, `application.properties`.
   - Dockerfile EXPOSE directives.
4. **Environment variables**: Collect all environment variables the application references. Classify each as:
   - Non-sensitive configuration (suitable for ConfigMap).
   - Sensitive data (requires Secret).
5. **Persistent storage**: Check for file system writes, database connections, upload directories, or cache paths that need persistent volumes.
6. **External dependencies**: Identify databases, caches, message queues, and external services the application connects to.

Record all findings for use in manifest generation.

## Step 2: Determine Resource Requirements

Estimate CPU and memory requirements based on the application type and runtime.

| Runtime | Default CPU Request | Default CPU Limit | Default Memory Request | Default Memory Limit |
|---------|--------------------|--------------------|----------------------|---------------------|
| Node.js | 100m | 500m | 128Mi | 512Mi |
| Python | 100m | 500m | 128Mi | 512Mi |
| Go | 50m | 250m | 64Mi | 256Mi |
| Java | 250m | 1000m | 512Mi | 1Gi |
| Rust | 50m | 250m | 64Mi | 256Mi |
| Ruby | 100m | 500m | 256Mi | 512Mi |
| .NET | 100m | 500m | 256Mi | 512Mi |

Adjust these defaults based on:

- Dockerfile memory settings (e.g., `NODE_OPTIONS=--max-old-space-size`).
- JVM heap configuration (`-Xmx`, `-Xms`).
- Application complexity (number of dependencies, framework overhead).
- User-specified requirements if provided.

These are starting recommendations. Instruct the user to refine them based on observed production metrics.

## Step 3: Generate Deployment Manifest

Construct the Deployment resource. Use `filesystem` to write the output file.

Required fields:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: <app-name>
  labels:
    app.kubernetes.io/name: <app-name>
    app.kubernetes.io/version: <version>
    app.kubernetes.io/managed-by: kubectl
spec:
  replicas: <count>
  selector:
    matchLabels:
      app.kubernetes.io/name: <app-name>
  template:
    metadata:
      labels:
        app.kubernetes.io/name: <app-name>
    spec:
      containers:
        - name: <app-name>
          image: <image>:<tag>
          ports:
            - containerPort: <port>
          resources:
            requests:
              cpu: <value>
              memory: <value>
            limits:
              cpu: <value>
              memory: <value>
```

Include the following based on analysis:

1. **Liveness probe**: Configure an HTTP GET probe on the health endpoint if one exists, or a TCP socket probe on the main port. Set `initialDelaySeconds` based on expected startup time.
2. **Readiness probe**: Configure separately from the liveness probe. Use a dedicated readiness endpoint if available, otherwise mirror the liveness probe with a shorter period.
3. **Startup probe**: For slow-starting applications (Java, large Node.js apps), add a startup probe with generous `failureThreshold` to avoid premature restarts.
4. **Security context**: Set `runAsNonRoot: true`, `readOnlyRootFilesystem: true` (if feasible), and `allowPrivilegeEscalation: false`.
5. **Environment variables**: Reference ConfigMap and Secret resources for all environment variables.
6. **Volume mounts**: Attach PersistentVolumeClaims for any identified persistent storage needs. Use `emptyDir` for temporary scratch space.
7. **Image pull policy**: Set to `IfNotPresent` for tagged images, `Always` for `latest` tags (and note that using `latest` in production is discouraged).

## Step 4: Generate Service Manifest

Create a Service resource to expose the application within the cluster.

- **Type**: Default to `ClusterIP` for internal services. Use `LoadBalancer` if the user specifies external access without an ingress controller. Use `NodePort` only if explicitly requested.
- **Ports**: Map each container port. Name ports according to the protocol (e.g., `http`, `grpc`, `metrics`).
- **Selector**: Match the Deployment's pod labels.
- **Session affinity**: Set `sessionAffinity: ClientIP` if the application uses server-side sessions. Otherwise, leave as `None`.

If the application exposes a metrics endpoint (e.g., `/metrics` for Prometheus), generate a second Service or annotate the primary Service with Prometheus scraping annotations:

```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "<metrics-port>"
    prometheus.io/path: "/metrics"
```

## Step 5: Generate Ingress Manifest

If the application serves HTTP traffic and should be externally accessible, generate an Ingress resource.

- Set `ingressClassName` based on the target environment (common values: `nginx`, `traefik`, `alb`).
- Configure TLS if the user specifies a domain name. Reference a Secret for the TLS certificate or use cert-manager annotations for automatic provisioning.
- Define path-based or host-based routing rules.
- Add relevant annotations for the ingress controller in use.

| Ingress Controller | Common Annotations |
|-------------------|-------------------|
| nginx | `nginx.ingress.kubernetes.io/rewrite-target`, `nginx.ingress.kubernetes.io/ssl-redirect` |
| traefik | `traefik.ingress.kubernetes.io/router.entrypoints`, `traefik.ingress.kubernetes.io/router.tls` |
| AWS ALB | `alb.ingress.kubernetes.io/scheme`, `alb.ingress.kubernetes.io/target-type` |

If the ingress controller is unknown, generate a minimal Ingress with a comment instructing the user to add controller-specific annotations.

## Step 6: Generate ConfigMap and Secret Manifests

Separate configuration data into ConfigMap (non-sensitive) and Secret (sensitive) resources.

**ConfigMap**:
- Include all non-sensitive environment variables.
- Include configuration files that the application reads from disk (mount as volumes).
- Use meaningful key names that match the environment variable names the application expects.

**Secret**:
- Include database credentials, API keys, tokens, and other sensitive values.
- Use `stringData` for readability in the manifest template, noting that Kubernetes stores them as base64-encoded `data` internally.
- Mark each secret value with a placeholder (`<REPLACE_WITH_ACTUAL_VALUE>`) rather than including real credentials.
- Add a comment listing which secrets need to be populated before deployment.

If the project uses an external secret manager (AWS Secrets Manager, HashiCorp Vault, Azure Key Vault), generate an ExternalSecret resource instead of a native Secret, using the appropriate CRD format.

## Step 7: Generate HorizontalPodAutoscaler

If the target environment is staging or production, generate an HPA resource.

- Set `minReplicas` and `maxReplicas` based on expected load:
  - Development: skip HPA (single replica is sufficient).
  - Staging: 1-3 replicas.
  - Production: 2-10 replicas (adjust based on user input).
- Configure scaling metrics:
  - CPU utilization target: 70% (default).
  - Memory utilization target: 80% (if memory-bound).
  - Custom metrics if the application exposes request rate or queue depth.
- Set `behavior` to control scale-up and scale-down rates, preventing thrashing.

## Step 8: Generate PersistentVolumeClaim (If Needed)

If Step 1 identified persistent storage requirements, generate PVC manifests.

- Set `accessModes` based on usage: `ReadWriteOnce` for single-pod access, `ReadWriteMany` if multiple pods need concurrent access.
- Set `storageClassName` to the cluster's default or a user-specified storage class.
- Set `resources.requests.storage` based on estimated needs.
- Add a comment explaining what data the volume holds and retention expectations.

## Step 9: Generate NetworkPolicy (If Applicable)

For production environments, generate a NetworkPolicy to restrict pod communication.

- Default deny all ingress traffic.
- Allow ingress from the Ingress controller namespace on the application port.
- Allow ingress from specific namespaces if the application serves internal API consumers.
- Allow egress to identified external dependencies (databases, external APIs).
- Allow egress to DNS (port 53, UDP and TCP) for name resolution.

## Step 10: Assemble and Validate Output

Collect all generated manifests and write them to the output directory.

**Plain Kubernetes YAML**:
- Write each resource to a separate file: `deployment.yaml`, `service.yaml`, `ingress.yaml`, `configmap.yaml`, `secret.yaml`, `hpa.yaml`, `pvc.yaml`, `networkpolicy.yaml`.
- Create a `kustomization.yaml` that references all resource files for easy application with `kubectl apply -k`.

**Helm Chart** (if requested):
- Create the chart directory structure: `Chart.yaml`, `values.yaml`, `templates/`.
- Move resource manifests to `templates/` with Helm template syntax for configurable values.
- Populate `values.yaml` with all configurable parameters and their defaults.
- Add `NOTES.txt` with post-install instructions.

Use `shell` to run `kubectl apply --dry-run=client -f <file>` for each manifest if `kubectl` is available, to validate syntax. Report any validation errors.

Present the user with a summary of all generated files and their purposes.

## Edge Cases

- **Multiple containers**: If the application requires sidecar containers (log shippers, proxies, init containers), generate a multi-container pod spec. Init containers run before the main application and are useful for database migrations or dependency checks.
- **StatefulSet vs Deployment**: If the application requires stable network identities or ordered scaling (databases, message brokers), generate a StatefulSet instead of a Deployment. Document the different update and scaling behavior.
- **DaemonSet**: If the application should run on every node (monitoring agents, log collectors), generate a DaemonSet. Omit replica count and HPA.
- **CronJob**: If the application is a periodic batch job rather than a long-running service, generate a CronJob manifest with the appropriate schedule.
- **Existing cluster resources**: Ask whether the namespace already exists or should be created. Check whether services like databases are already running in the cluster to avoid duplicating them.
- **Air-gapped environments**: If the cluster has no internet access, note that all container images must be available in an internal registry and adjust image references accordingly.

## Related Skills

- **deployment-checklist** (eskill-devops): Follow up with deployment-checklist after this skill to validate that generated manifests meet deployment requirements.
- **monitoring-config** (eskill-devops): Follow up with monitoring-config after this skill to add observability to the generated Kubernetes workloads.

variable "TAG" {
  default = "latest"
}

variable "BEDROCK_BPFTRACE" {
  default = "v0.0.0-stable"
}

group "default" {
  targets = ["bedrock"]
}

target "bedrock" {
  context    = "."
  dockerfile = "build/Dockerfile"

  tags = [
    "ghcr.io/amirhnajafiz/bedrock-tracer:${TAG}",
    "ghcr.io/amirhnajafiz/bedrock-tracer:latest"
  ]

  output = ["type=registry"]

  args = {
    BEDROCK_BPFTRACE = BEDROCK_BPFTRACE
  }
}

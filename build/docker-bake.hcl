variable "TAG" {
  default = "latest"
}

variable "BEDROCK_BPFTRACE" {
  default = "s0.1.0"
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

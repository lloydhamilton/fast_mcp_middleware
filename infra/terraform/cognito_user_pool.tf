resource "aws_cognito_user_pool" "m2m_pool" {
  name = "fastmcp-user-pool"

  admin_create_user_config {
    allow_admin_create_user_only = true
  }

  auto_verified_attributes = []
  alias_attributes         = []
  mfa_configuration        = "OFF"

  password_policy {
    minimum_length    = 12
    require_lowercase = true
    require_uppercase = true
    require_numbers   = true
    require_symbols   = false
  }
}
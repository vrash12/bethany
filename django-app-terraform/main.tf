provider "aws" {
  region = "ap-southeast-2"  # Use the correct AWS region
}

# Use an existing security group
data "aws_security_group" "existing_sg" {
  id = "sg-04dcb02ef3d932172"  # ID of your existing security group
}

resource "aws_instance" "django_server" {
  ami           = "ami-03f0544597f43a91d"  # Ensure this AMI ID is correct for ap-southeast-2
  instance_type = "t2.micro"  # Change as needed

  key_name = "bethany"  # Your EC2 key pair name

  # Use the existing security group
  vpc_security_group_ids = [data.aws_security_group.existing_sg.id]

  tags = {
    Name = "bethany"
  }

  # User data for initializing the instance
  user_data = <<-EOF
              #!/bin/bash
              sudo yum update -y
              sudo yum install python3 -y
              sudo pip3 install django gunicorn
              sudo amazon-linux-extras install nginx1.12 -y
              # Additional setup commands
              EOF
}

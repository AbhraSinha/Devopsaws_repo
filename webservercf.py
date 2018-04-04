from troposphere import Ref, Template, Parameter, Output, Join, GetAtt, Base64
import troposphere.ec2 as ec2

t=Template()

#Security Group
#AMI id and instance type
#SSH KEypair

sg = ec2.SecurityGroup("Test1")
sg.GroupDescription = "Allow access through porty 80 and 22 to the web instance"
sg.SecurityGroupIngress = [
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "22", ToPort = "22", CidrIp= "0.0.0.0/0"),
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "80", ToPort = "80", CidrIp= "0.0.0.0/0"),
]

t.add_resource(sg)

keypair = t.add_parameter(Parameter(
	"Keyname",
	Description = "SSH Keypair to access the instance",
	Type = "String"
	))

instance = ec2.Instance("Webserver")
instance.ImageId = "ami-1853ac65"
instance.InstanceType = "t2.micro"
instance.SecurityGroups = [Ref(sg)]
instance.KeyName = Ref(keypair)
#Ref is part of CF

ud = Base64(Join('\n',
	[
		"#!/bin/bash",
		"sudo yum -y install httpd",
		"sudo echo '<html><body><h1>Welcome to DevOps on AWS</h1></body></html>' > /var/www/html/test.html",
		"sudo service http start",
		"sudo chkconfig httpd on"
		]))

instance.UserData = ud

t.add_resource(instance)

t.add_output(Output(
	"InstanceAccess",
	Description = "Command to use to access the Instance using SSH",
	Value = Join ("", ["ssh -i ~/.ssh/Test1.pem ec2-user@", GetAtt(instance, "PublicDnsName")])
	))

t.add_output(Output(
	"WebURL",
	Description = "URL of the webserver",
	Value = Join("",["http://",GetAtt(instance, "PublicDnsName")])
	))


print(t.to_json())
from troposphere import Ref, Template, Parameter, Output, Join, GetAtt, Base64
import troposphere.ec2 as ec2

t=Template()

#Security Group
#AMI id and instance type
#SSH KEypair

sg = ec2.SecurityGroup("test1")
sg.GroupDescription = "Allow access through porty 8080 and 22 to the web instance"
sg.SecurityGroupIngress = [
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "22", ToPort = "22", CidrIp= "0.0.0.0/0"),
	ec2.SecurityGroupRule(IpProtocol = "tcp", FromPort = "8080", ToPort = "8080", CidrIp= "0.0.0.0/0"),
]

t.add_resource(sg)

keypair = t.add_parameter(Parameter(
	"Keyname",
	Description = "SSH Keypair to access the instance",
	Type = "String"
	))
instance = ec2.Instance("Jenkins")
instance.ImageId = "ami-1853ac65"
instance.InstanceType = "t2.micro"
instance.SecurityGroups = [Ref(sg)]
#instance.IamInstanceProfile-Ref("InstanceProfile")
instance.KeyName = Ref(keypair)
#Ref is part of CF

t.add_resource(instance)

t.add_output(Output(
	"InstanceAccess",
	Description = "Command to use to access the Instance using SSH",
	Value = Join ("", ["ssh -i ~/.ssh/Test1.pem ec2-user@", GetAtt(instance, "PublicDnsName")])
	))
t.add_output(Output(
	"WebURL",
	Description = "URL of the webserver",
	Value = Join("",["http://",GetAtt(instance, "PublicDnsName"),":8080"])
	))
print(t.to_json())
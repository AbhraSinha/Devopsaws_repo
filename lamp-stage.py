from troposphere import Ref, Template, Parameter, Output, Join, GetAtt, Base64
from troposphere.iam import InstanceProfile, PolicyType as IAMPolicy, Role
from awacs.aws import Action, Allow, Policy, Principal, Statement
from awacs.sts import AssumeRole

import troposphere.ec2 as ec2

t=Template()

#Security Group
#AMI id and instance type
#SSH KEypair

sg = ec2.SecurityGroup("test1")
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

instance = ec2.Instance("Staging1")
instance.ImageId = "ami-1853ac65"
instance.InstanceType = "t2.micro"
instance.SecurityGroups = [Ref(sg)]
#instance.IamInstanceProfile-Ref("InstanceProfile")
instance.KeyName = Ref(keypair)
#Ref is part of CF

#Policy Document
principal = Principal("Service",["ec2.amazonaws.com"])
statement = Statement(Effect=Allow,Action=[AssumeRole],Principal=principal)
policy = Policy(Statement=[statement])
role = Role("Role",AssumeRolePolicyDocument=policy)

t.add_resource(role)
t.add_resource(
    InstanceProfile(
        "InstanceProfile",
        Path="/",
        Roles=[Ref("Role")]
    )
)

t.add_resource(IAMPolicy(
    "Policy",
    PolicyName = "AllowS3",
    PolicyDocument=Policy(
        Statement=[
            Statement(
                Effect=Allow, Action=[Action("s3","*")],
                Resource=["*"]
                )
            ]
        ),
        Roles=[Ref("Role")]
    ))

instance.IamInstanceProfile = Ref("InstanceProfile")

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
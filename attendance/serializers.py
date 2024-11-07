from rest_framework import serializers
from .models import (
    Member, 
    Attendance, 
    Service, 
    MinisterAttendance, 
    SmallGroup, 
    SmallGroupMembership, 
    SmallGroupAttendance, 
    Giving
)

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    member = MemberSerializer(read_only=True)
    service = ServiceSerializer(read_only=True)
    member_id = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all(), source='member', write_only=True)
    service_id = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), source='service', write_only=True)

    class Meta:
        model = Attendance
        fields = ['id', 'member', 'service', 'member_id', 'service_id', 'date', 'status']

class MinisterAttendanceSerializer(serializers.ModelSerializer):
    minister_id = serializers.PrimaryKeyRelatedField(queryset=Minister.objects.all(), source='minister', write_only=True)

    class Meta:
        model = MinisterAttendance
        fields = ['id', 'minister', 'service', 'minister_id', 'date', 'status']

class SmallGroupSerializer(serializers.ModelSerializer):
    leader_id = serializers.PrimaryKeyRelatedField(queryset=Minister.objects.all(), source='leader', write_only=True)

    class Meta:
        model = SmallGroup
        fields = ['id', 'name', 'leader', 'leader_id']

class SmallGroupMembershipSerializer(serializers.ModelSerializer):
    small_group_id = serializers.PrimaryKeyRelatedField(queryset=SmallGroup.objects.all(), source='small_group', write_only=True)

    class Meta:
        model = SmallGroupMembership
        fields = ['id', 'small_group', 'member', 'minister', 'small_group_id', 'joined_at']

class SmallGroupAttendanceSerializer(serializers.ModelSerializer):
    small_group_id = serializers.PrimaryKeyRelatedField(queryset=SmallGroup.objects.all(), source='small_group', write_only=True)

    class Meta:
        model = SmallGroupAttendance
        fields = ['id', 'small_group', 'small_group_id', 'date', 'members', 'ministers', 'attended']

class GivingSerializer(serializers.ModelSerializer):
    member_id = serializers.PrimaryKeyRelatedField(queryset=Member.objects.all(), source='member', write_only=True)
    minister_id = serializers.PrimaryKeyRelatedField(queryset=Minister.objects.all(), source='minister', write_only=True)

    class Meta:
        model = Giving
        fields = ['id', 'member', 'minister', 'member_id', 'minister_id', 'date', 'amount', 'purpose', 'notes']

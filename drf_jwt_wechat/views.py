#!/usr/bin/env python
# coding=utf-8
# connect='li233111@gmail.com'
__auther__ = 'liazylee'

from rest_framework_jwt.views import ObtainJSONWebToken

# import emoji as emoji
import requests
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _
from rest_framework_jwt.compat import get_username_field
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
User = get_user_model()



class Serializer(serializers.Serializer):
    @property
    def object(self):
        return self.validated_data


class JSONWechatTokenSerializer(Serializer):
    """
    通过小程序post请求发送code, 经JSONWechatTokenSerializer验证后返回
    openid和session_key.
    使用用户标识openid生成一个user实例, 方便视图对用户权限的管理.
    """

    def __init__(self, *args, **kwargs):
        super(JSONWechatTokenSerializer, self).__init__(*args, **kwargs)
        self.fields['code'] = serializers.CharField()
        """
        userinfo的信息存在此处
        """
        # self.fields['nickName'] = serializers.CharField(allow_null=True, )
        # self.fields['gender'] = serializers.IntegerField(allow_null=True, )
        # self.fields['language'] = serializers.CharField(allow_null=True, )
        # self.fields['city'] = serializers.CharField(allow_null=True, )
        # self.fields['province'] = serializers.CharField(allow_null=True)
        # self.fields['country'] = serializers.CharField(allow_null=True, )
        # self.fields['avatarUrl'] = serializers.CharField(allow_null=True, )

    @property
    def username_field(self):
        return get_username_field()

    def validate(self, attrs):
        code = attrs.get('code')
        result = self._credentials_validation(code)
        user = self._get_or_create_user(result['openid'], result['session_key'])
        attrs['username'] = result['openid']
        attrs['password'] = result['openid']
        self._update_userinfo(user, attrs)
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = authenticate(**credentials)
            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "userinfo" and "code"')
            raise serializers.ValidationError(msg)

    # @staticmethod
    # def _update_userinfo(user, attrs):
    #     try:
    #         UserInfo.objects.filter(user=user).update(avatar_url=attrs.get('avatarUrl'), gender=attrs.get('gender'),
    #                                                   province=attrs.get('province'), city=attrs.get('city'),
    #                                                   country=attrs.get('country'),
    #                                                   nick_name=emoji.demojize(attrs.get('nickName')),
    #                                                   language=attrs.get('language'))
    #     except Exception as e:
    #         """
    #         无测试，故放入此try"""
    #         print(e, 111)
    #         UserInfo.objects.create(user=user, avatar_url=attrs.get('avatarUrl'), gender=attrs.get('gender'),
    #                                 province=attrs.get('province'), city=attrs.get('city'),
    #                                 country=attrs.get('country'), nick_name=emoji.demojize(attrs.get('nickName')))

    @staticmethod
    def _get_or_create_user(openid, session_key):
        user, _ = User.objects.get_or_create(
            username=openid,
            defaults={'password': openid}
        )
        user.set_password(openid)
        user.first_name = session_key
        user.save()
        return user

    @staticmethod
    def _credentials_validation(code):
        # 成功拿到openid和session_key并返回
        req_params = {
            'appid': settings.APP_ID,
            'secret': settings.APP_SECRET,
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        url = 'https://api.weixin.qq.com/sns/jscode2session'

        response = requests.get(url, params=req_params)
        result = response.json()

        if 'errcode' in result:
            msg = _(result['errmsg'])
            raise serializers.ValidationError(msg, code='authorization')
        return result


class ObtainJSONWechatToken(ObtainJSONWebToken):
    serializer_class = JSONWechatTokenSerializer


obtain_jwt_token = ObtainJSONWechatToken.as_view()

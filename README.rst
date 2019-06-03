drf-jwt-wechat
==============
**drf-jwt-wechat 是在jwt，跟rest_framework_jwt基础上进行修改过的，用于微信小程序登录，
前端只需post方法传code即可进行jwt登录验证**

Usage
-----
*在django项目settings中添加修改APP_ID=xxxx，APP_SECRET=xxxxx,以及跟rest_framework_jwt包同样配置如下*
::

    REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),

在url中引用
::

    from drf-jwt-wechat.views import obtain_jwt_token
    #...

    urlpatterns = [
        '',
        # ...

        url(r'^api-token-auth/', obtain_jwt_token),
    ]

后续
----
因为水平有限，目前只有登录，没有Refresh Token，以及Verify Token，不影响rest_framework_jwt的api使用。
任何问题请联系 https://github.com/liazylee/ 源码详解 https://blog.csdn.net/liazylee/article/details/90717939
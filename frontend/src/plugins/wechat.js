import Vue from 'vue'

function checkStatus(res, options = {}) {
    let { r, msg } = res.data;
    let type, message;
    if (r !== 0) {
        type = 'error';
        message = msg;
    } else {
        type = 'success';
        message = '提交成功';
    }
    this.$message({
        message: message,
        type: type
    });
}

function eventSourceListener(puid) {

    console.log(puid);
    // puid is redis channel name to get event message
    // let source = new EventSource(`http://127.0.0.1:8000/wechat/api/stream/${puid}/`);
    let source = new EventSource(`http://127.0.0.1:8000/wechat/api/stream/wechat/`);
    // console.log(source);
    let self = this;
    // self.eventSource = source;
    // console.log(self);

    source.addEventListener('login', function(event) {
        let data = JSON.parse(event.data);
        console.log('login event data:');
        console.log(data);
        if (data.type == 'scan_qr_code') {
            self.uuid = data.uuid;
            self.qrCode = `data:image/png;base64,${data.extra}`;
        } else if (data.type == 'confirm_login') {
            self.sub_title = 'Scan successful';
            self.sub_desc = 'Confirm login on mobile WeChat';
            self.qrCode = data.extra;
        } else if (data.type == 'logged_in') {
            sessionStorage.setItem('user', JSON.stringify(data.user));
            self.$router.push({ path: '/friendlist' });
        } else if (data.type == 'logged_out') {
            sessionStorage.removeItem('user');
            self.$router.push('/login');
        }
    }, false);

    source.addEventListener('notification', function(event) {
        console.log('event', event);
        let data = JSON.parse(event.data);
        console.log(event.data);
        self.notificationCount = data.count;
    }, false);

    source.addEventListener('error', function(event) {
        console.log(event);
        console.log("Failed to connect to event stream");
    }, false);

    return source;
}

export default {
    install(Vue, defaultOptions = {}) {
        Vue.mixin({
            data: function() {
                return {
                    uuid: '',
                    qrCode: `http://localhost:8000/static/img/qr_code.png`,
                    sub_title: 'Scan to log in to WeChat',
                    sub_desc: 'Log in on phone to use WeChat on Web',
                    notificationCount: 0,
                }
            }
        }),
        Vue.prototype.$checkStatus = checkStatus;
        Vue.prototype.$eventSourceListener = eventSourceListener;
    }
}

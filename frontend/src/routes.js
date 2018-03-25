import Login from './views/Login.vue'
import NotFound from './views/404.vue'
import Home from './views/Home.vue'
import FriendList from './views/nav1/FriendList.vue'
import MPList from './views/nav1/MPList.vue'
import GroupList from './views/nav1/GroupList.vue'
import RecMsgList from './views/nav2/RecMsgList.vue'
import SndMsgList from './views/nav2/SndMsgList.vue'

let routes = [
    {
        path: '/login',
        component: Login,
        name: '',
        hidden: true
    },
    {
        path: '/404',
        component: NotFound,
        name: '',
        hidden: true
    },
    {
        path: '/',
        component: Home,
        name: '好友',
        iconCls: 'fa fa-id-card-o',//图标样式class
        children: [
            { path: '/friendlist', component: FriendList, name: '好友列表' },
        ]
    },
    {
        path: '/',
        component: Home,
        name: '群组',
        iconCls: 'fa fa-id-card-o',//图标样式class
        children: [
            { path: '/grouplist', component: GroupList, name: '群组列表' },
        ]
    },
    {
        path: '/',
        component: Home,
        name: '公众号',
        iconCls: 'fa fa-id-card-o',//图标样式class
        children: [
            { path: '/mplist', component: MPList, name: '公众号' },
        ]
    },
    {
        path: '/',
        component: Home,
        name: '消息',
        iconCls: 'el-icon-message',
        children: [
            { path: '/recmsglist', component: RecMsgList, name: '接收消息' },
            { path: '/sndmsglist', component: SndMsgList, name: '发送消息' }
        ]
    },
    {
        path: '*',
        hidden: true,
        redirect: { path: '/404' }
    }
];

export default routes;
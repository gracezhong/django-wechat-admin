import axios from 'axios';

// let base = 'http://localhost:8000/wechat/api';
let base = '/wechat/api';

const request = (url, options={}, method='get') => {
    let key = ~['delete', 'get', 'head'].indexOf(method) ? 'params' : 'data';
    return axios(Object.assign({'url': url, 'method':method, 'validateStatus': false}, {[key]: options}))
        .then(res => res)
        .catch(function (error) {
            // console.log(error.config);
            if (error.response) {
                // The request was made and the server responded with a status code
                // that falls out of the range of 2xx
                // console.log(error.response.data);
                // console.log(error.response.status);
                // console.log(error.response.headers);
                return error.response;
            } else if (error.request) {
                // The request was made but no response was received
                // `error.request` is an instance of XMLHttpRequest in the browser and an instance of
                // http.ClientRequest in node.js
                // console.log(error.request);
                return error.request;
            } else {
                // Something happened in setting up the request that triggered an Error
                // console.log('Error', error.message);
                return error.message;
            }
        });
};

export const Login = params => {
    return request(`${base}/login/`, params, 'post')
};

export const logOut = params => {
    return request(`${base}/logout/`, params, 'post')
};

export const getFriendListPage = params => {
    return request(`${base}/friends/`, params);
};

export const getMPListPage = params => {
    return request(`${base}/mps/`, params)
};

export const getGroupListPage = params => {
    // return axios.get(`${base}/groups/`, { params: params });
    return request(`${base}/groups/`, params)
};

export const editFriend = params => {
    return request(`${base}/friend/${params.puid}`, params, 'patch')
};

export const getMsgListPage = params => {
    return request(`${base}/messages/`, params)
};

export const sendMessage = params => {
    console.log("3: batch Message test");
    return request(`${base}/messages/`, params, 'post')
};

function makeRequest(params) {
    console.log("3: batch Message test");
    return axios.post(`${base}/messages/`, params);
}

export const batchSendMessage = param_list => {
    console.log("1: batch Message test");
    let requests = param_list.map(makeRequest);
    console.log("2: batch Message test");
    console.log(requests);
    return axios.all(requests).then(axios.spread(function (res){
        // res => res.data;
        console.log("4: batch Message test");
        console.log(res);
        // console.log(res.data);
    }));
};



// function makeRequest(id) {
//     let url = `${base}/friend/${id}`;
//     return axios.delete(url);
// }


// export const batchRemoveUser = params => {
//     let ids = params.ids.split(",");
//     console.log(ids);
//     let requests = ids.map(makeRequest);
//     return axios.all(requests).then(axios.spread(function (res){
//         res => res.data;
//         console.log(res);
//     }));
// };

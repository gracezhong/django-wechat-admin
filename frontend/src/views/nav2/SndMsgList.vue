<template>
	<section>
		<!--工具条-->
		<el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
			<el-form :inline="true" :model="filters">
				<el-form-item>
					<el-input v-model="filters.content" placeholder="消息内容" clearable></el-input>
				</el-form-item>
				<el-form-item>
					<el-button type="primary" v-on:click="getMsgs">查询</el-button>
				</el-form-item>
			</el-form>
		</el-col>

		<!--列表-->
		<el-table :data="msgs" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
			<el-table-column type="selection" width="55">
			</el-table-column>
			<el-table-column prop="group" label="群聊" width="160">
				<template slot-scope="scope">
					<div v-if="!isEmptyObject(scope.row.group)">
						<img :src="formatAvatar(scope.row.group)" class="avatar" v-if="scope.row.group.avatar"/>
						<!--<a :href="'/#/group/' + scope.row.group.id" class="nick-name">{{scope.row.group.nick_name}}</a>-->
						{{scope.row.group.nick_name}}
					</div>
				</template>
			</el-table-column>
			<el-table-column prop="receiver" label="接收人" width="160">
				<template slot-scope="scope">
					<div v-if="!isEmptyObject(scope.row.receiver)">
						<img :src="formatAvatar(scope.row.receiver)" class="avatar" v-if="scope.row.receiver.avatar"/>
						<!--<a href="#" class="nick-name">{{scope.row.sender.nick_name}}</a>-->
						{{scope.row.receiver.nick_name}}
					</div>
				</template>
			</el-table-column>

			<el-table-column prop="content" label="内容" min-width="400" sortable>
				<template slot-scope="scope">
					<div v-if="scope.row.url">
						<a :href="scope.row.url" target="_blank" class="content">{{scope.row.content}}</a>
					</div>
					<!-- Picture-->
					<div v-else-if="scope.row.type == 6">
						<img :src="formatSource(scope.row)" class="picture"/>
					</div>
					<!-- Recording -->
					<div v-else-if="scope.row.type == 7">
						<audio controls="controls"><source :src="formatSource(scope.row)" /></audio>
						<!--<embed height="100" width="100" :src="formatSource(scope.row)" />-->
					</div>
					<!-- Video-->
					<div v-else-if="scope.row.type == 9">
						<video controls="controls" :src="formatSource(scope.row)" class="video"></video>
					</div>
					<!-- Card and other types of message-->
					<div v-else>{{ scope.row.type == 3 ? '名片：' : '' }} {{scope.row.content}}</div>
				</template>
			</el-table-column>
			<el-table-column prop="receive_time" label="时间" width="300" sortable>
			</el-table-column>
			<el-table-column label="操作" min-width="150">
				<template slot-scope="scope">
					<el-button type="danger" size="small" @click="handleDel(scope.row)">删除</el-button>
				</template>
			</el-table-column>
		</el-table>

		<!--工具条-->
		<el-col :span="24" class="toolbar">
			<el-button type="danger" @click="batchRemove" :disabled="this.sels.length===0">删除消息</el-button>
			<el-pagination background layout="prev, pager, next" @size-change="handleSizeChange" @current-change="handleCurrentChange" :page-size="pageSize" :total="total" style="float:right;">
			</el-pagination>
		</el-col>

	</section>
</template>

<script>
    import util from '../../common/js/util'
    import { getMsgListPage } from '../../api/api';

    export default {
        data() {
            return {
                filters: {
                    content: ''
                },
                msgs: [],
                total: 0,
                page: 1,
                pageSize: 20,
                listLoading: false,
                sels: [],//列表选中列
            }
        },
        methods: {
            isEmptyObject( obj ) {
                for ( var name in obj ) {
                    return false;
                }
                return true;
            },
            handleSizeChange(val) {
                this.pageSize = val;
            },
            handleCurrentChange(val) {
                this.page = val;
                this.getMsgs();
            },
            formatSource: function(row) {
                // console.log(row.file_ext);
                return 'http://localhost:8000/static/msg_uploads/' + row.id + row.file_ext;
            },
            formatAvatar: function(obj) {
                // console.log(row);
                return  "http://localhost:8000" + obj.avatar;
            },
            //获取接收消息列表
            getMsgs() {
                let user = sessionStorage.getItem('user');
                user = JSON.parse(user);
                console.log(user);
                let para = {
                    page: this.page,
                    page_size: this.pageSize,
                    content__contains: this.filters.content,
                    sender_id: user.puid
                };
                console.log(para);
                this.listLoading = true;
                getMsgListPage(para).then((res) => {

                    if (res.status< 400) {
                        console.log("get page data");
                        console.log(res);
                        this.total = res.data.count;
                        this.msgs = res.data.results;
                        this.listLoading = false;
					}
					else {
                        console.log(res.data);
                        this.$message({
                            message: res.data,
                            type: 'error',
                            showClose: true
                        });
					}
                });
            },
            selsChange: function (sels) {
                this.sels = sels;
            },
            handleDel: function (row) {
                this.$confirm('确认删除该信息吗?', '提示', {
                    type: 'warning'
                }).then(() => {
                    this.listLoading = true;
                    let para = { id: row.id };
                    removeMsg(para).then((res) => {
                        this.listLoading = false;
                        console.log(res);
                        this.$message({
                            message: '删除成功',
                            type: 'success'
                        });
                        this.getMsgs();
                    });
                }).catch(() => {

                });
            },
            //批量删除
            batchRemove: function () {
                var ids = this.sels.map(item => item.id).toString();
                this.$confirm('确认删除选中消息吗？', '提示', {
                    type: 'warning'
                }).then(() => {
                    this.listLoading = true;
                    let para = { ids: ids };
                    console.log(para.ids);
                    batchRemoveMsgs(para).then((res) => {
                        this.listLoading = false;
                        this.$message({
                            message: '删除成功',
                            type: 'success'
                        });
                        this.getMsgs();
                    });
                }).catch(() => {

                });
            }
        },
        mounted() {
            this.getMsgs();
        }
    }

</script>

<style scoped>
	.avatar {
		width: 40px;
		height: 40px;
		border-radius: 5px;
		margin: 10px 0px 5px 0px;
	}
	.picture {
		max-height: 120px;
	}
	.video {
		max-width: 160px;
	}
</style>
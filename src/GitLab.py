import os
import requests

class GitLab:
    def __init__(self, token=None):
        self.token = token or os.environ.get('GITLAB_TOKEN')
        if not self.token:
            raise Exception('GITLAB_TOKEN 환경 변수가 설정되어 있지 않습니다.')
        self.api_url = 'https://gitlab.com/api/v4/projects'
        self.headers = {'PRIVATE-TOKEN': self.token}

    def create_project(self, name, visibility='private', success_msg=None, fail_msg=None):
        data = {
            'name': name,
            'visibility': visibility
        }
        response = requests.post(self.api_url, headers=self.headers, data=data)
        if response.status_code == 201:
            if success_msg:
                print(success_msg)
            return response.json()
        else:
            if fail_msg:
                print(fail_msg)
            print('상태 코드:', response.status_code)
            print('응답 내용:', response.text)
            return None

    def create_milestone(self, project_id, title, description='', due_date=None, success_msg=None, fail_msg=None):
        milestone_data = {
            'title': title,
            'description': description
        }
        if due_date:
            milestone_data['due_date'] = due_date
        milestone_url = f"{self.api_url}/{project_id}/milestones"
        response = requests.post(milestone_url, headers=self.headers, data=milestone_data)
        if response.status_code == 201:
            if success_msg:
                print(success_msg)
            return response.json()
        else:
            if fail_msg:
                print(fail_msg)
            print('상태 코드:', response.status_code)
            print('응답 내용:', response.text)
            return None

    def create_issue(self, project_id, title, description='', milestone_id=None, success_msg=None, fail_msg=None):
        issue_data = {
            'title': title,
            'description': description
        }
        if milestone_id:
            issue_data['milestone_id'] = milestone_id
        issue_url = f"{self.api_url}/{project_id}/issues"
        response = requests.post(issue_url, headers=self.headers, data=issue_data)
        if response.status_code == 201:
            if success_msg:
                print(success_msg)
            return response.json()
        else:
            if fail_msg:
                print(fail_msg)
            print('상태 코드:', response.status_code)
            print('응답 내용:', response.text)
            return None

    def invite_member(self, project_id, email, access_level=30, success_msg=None, fail_msg=None):
        """
        프로젝트에 사용자를 초대하는 함수
        :param project_id: 프로젝트 ID
        :param email: 초대할 사용자의 이메일
        :param access_level: 권한(기본: 30=Developer)
        :param success_msg: 성공 메시지
        :param fail_msg: 실패 메시지
        """
        invite_url = f"{self.api_url}/{project_id}/invitations"
        data = {
            'email': email,
            'access_level': access_level
        }
        response = requests.post(invite_url, headers=self.headers, data=data)
        if response.status_code == 201:
            if success_msg:
                print(success_msg)
            return response.json()
        else:
            if fail_msg:
                print(fail_msg)
            print('상태 코드:', response.status_code)
            print('응답 내용:', response.text)
            return None

    def get_project_by_name(self, project_name, success_msg=None, fail_msg=None):
        """
        프로젝트 이름만 받아서, 토큰의 사용자명과 결합해 프로젝트 정보를 조회
        :param project_name: 예) 'test-project-from-api'
        :param success_msg: 성공 메시지
        :param fail_msg: 실패 메시지
        :return: 프로젝트 정보(dict) 또는 None
        """
        # 1. 토큰으로 사용자명 조회
        user_url = 'https://gitlab.com/api/v4/user'
        user_response = requests.get(user_url, headers=self.headers)
        if user_response.status_code == 200:
            username = user_response.json()['username']
        else:
            if fail_msg:
                print(fail_msg)
            print('사용자명 조회 실패...')
            print('상태 코드:', user_response.status_code)
            print('응답 내용:', user_response.text)
            return None
        # 2. 사용자명과 프로젝트명 결합
        project_path = f'{username}/{project_name}'
        encoded_path = project_path.replace('/', '%2F')
        url = f'{self.api_url}/{encoded_path}'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            if success_msg:
                print(success_msg)
            return response.json()
        else:
            if fail_msg:
                print(fail_msg)
            print('상태 코드:', response.status_code)
            print('응답 내용:', response.text)
            return None

    def get_project_members(self, project_id, success_msg=None, fail_msg=None):
        """
        프로젝트에 참여하고 있는 멤버(사용자) 정보 조회
        :param project_id: 프로젝트 ID
        :param success_msg: 성공 메시지
        :param fail_msg: 실패 메시지
        :return: 멤버 정보 리스트(list of dict) 또는 None
        """
        url = f'{self.api_url}/{project_id}/members'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            if success_msg:
                print(success_msg)
            return response.json()
        else:
            if fail_msg:
                print(fail_msg)
            print('상태 코드:', response.status_code)
            print('응답 내용:', response.text)
            return None

# if __name__ == '__main__':
#     gitlab = GitLab()
#     # 1. 프로젝트 조회
#     project_info = gitlab.get_project_by_name(
#         project_name='test-project-from-api',
#         success_msg='프로젝트 조회 성공!',
#         fail_msg='프로젝트 조회 실패...'
#     )
    # if project_info:
    #     project_id = project_info['id']
    #     invitee_email = '20245459@vision.hoseo.edu'  # 실제 초대할 이메일로 변경 필요
    #     gitlab.invite_member(
    #         project_id=project_id,
    #         email=invitee_email,
    #         success_msg='초대 성공!',
    #         fail_msg='초대 실패...'
    #     )
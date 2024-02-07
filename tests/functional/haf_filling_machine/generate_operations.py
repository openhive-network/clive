from __future__ import annotations

import random

from generate_block_log import generate_random_text

import test_tools as tt
from schemas.operations.comment_operation import CommentOperation
from schemas.operations.comment_options_operation import CommentOptionsOperation
from schemas.operations.custom_json_operation import CustomJsonOperation
from schemas.operations.transfer_operation import TransferOperation
from schemas.operations.vote_operation import VoteOperation
from schemas.operations.extensions.comment_options_extensions import BeneficiaryRoute, CommentPayoutBeneficiaries


def draw_comment(comment_data: dict) -> tuple:
    random_element = random.randint(0, len(comment_data) - 1)
    permlink = list(comment_data.keys())[random_element]
    account_name = comment_data[permlink]
    return permlink, account_name


def generate_random_custom_json_as_string():
    avg_json_elements_number = 3
    elements = random.randint(1, avg_json_elements_number * 2)
    output_as_string = "{"
    for it in range(elements):
        key_name = generate_random_text(3, random.randint(3, 15))
        value = generate_random_text(5, 100) if it % 2 == 0 else random.randint(-1000000, 1000000)
        output_as_string += (
            '"' + key_name + '": ' + str(value) + ", "
            if isinstance(value, int)
            else '"' + key_name + '": "' + value + '", '
        )

    output_as_string = output_as_string[:-2]  # get rid of last comma and space
    output_as_string += "}"
    return output_as_string


def get_last_index_from(data_dict: dict) -> int:
    last_element = list(data_dict.keys())[-1]
    return int(last_element[last_element.rfind("-")+1:])


def __prepare_operation(
    account_name: str, comment_data: dict, comment_data_for_current_iteration: dict
) -> VoteOperation | CommentOperation | CustomJsonOperation | TransferOperation | CommentOptionsOperation:
    # range 0-24 -> transfer
    # range 25-49 -> vote
    # range 50-74 -> comment
    # range 75-100 -> custom json
    random_number = random.randint(0, 100)
    if 0 <= random_number < 25:
        return create_transfer(account_name)
    if 25 <= random_number < 50:
        return create_vote(
            account_name,
            comment_data,
        )
    if 50 <= random_number < 75:
        return create_comment_operation(account_name, comment_data, comment_data_for_current_iteration)
    return create_custom_json(account_name)


def create_transfer(from_account: str) -> TransferOperation:
    return TransferOperation(
        from_=from_account,
        to=from_account,
        amount=tt.Asset.Test(0.001),
        memo=generate_random_text(3, 200),
    )


def create_vote(account_name: str, comment_data: dict) -> VoteOperation:
    vote_weight = 0
    while vote_weight == 0:
        vote_weight = random.randint(-100, 100)

    permlink_to_vote_on, content_author = draw_comment(comment_data)
    return VoteOperation(voter=account_name, author=content_author, permlink=permlink_to_vote_on, weight=vote_weight)


def create_comment_operation(
    account_name: str, comment_data: dict, comment_data_for_current_iteration: dict
) -> CommentOperation:

    # 20% chance for creating new article instead of just reply
    if random.randint(0, 5) == 0:
        parent_comment_permlink = f"article-category-{generate_random_text(1, 10)}"
        parent_author = ""
    else:
        parent_comment_permlink, parent_author = draw_comment(comment_data)
    index = get_last_index_from(comment_data) if len(comment_data_for_current_iteration) == 0 else (
        get_last_index_from(comment_data_for_current_iteration))
    current_permlink = f"permlink-{index+1}"
    del comment_data[list(comment_data.keys())[0]]

    comment_data_for_current_iteration[current_permlink] = account_name

    return CommentOperation(
        parent_author=parent_author,
        parent_permlink=parent_comment_permlink,
        author=account_name,
        permlink=current_permlink,
        title=generate_random_text(5, 15),
        body=generate_random_text(5, 100),
        json_metadata="{}",
    )


def create_custom_json(account_name: str) -> CustomJsonOperation:
    return CustomJsonOperation(
        required_auths=[],
        required_posting_auths=[account_name],
        id_=generate_random_text(3, 32),
        json_=generate_random_custom_json_as_string(),
    )


def create_comment_options(account_name: str, comment_data_for_current_iteration: dict) -> CommentOptionsOperation:
    # comment options is created only with article
    author_of_comment = account_name
    index = get_last_index_from(comment_data_for_current_iteration)
    permlink = f"permlink-{index}"
    beneficiaries = []

    while len(beneficiaries) < 3:  # draw 3 accounts to be beneficiaries
        account_number = random.randint(0, 99_999)
        beneficiary_name = f"account-{account_number}"
        for beneficiary in beneficiaries:
            # avoid duplicating beneficiary and making comment author as beneficiary
            if beneficiary == beneficiary_name or beneficiary == account_name:
                continue
        beneficiaries.append(beneficiary_name)
    beneficiaries = sorted(beneficiaries)
    beneficiaries = [BeneficiaryRoute(account=beneficiary_name, weight=500) for beneficiary_name in beneficiaries]

    prepared_beneficiaries = CommentPayoutBeneficiaries(beneficiaries=beneficiaries)
    extensions = [{"type": "comment_payout_beneficiaries", "value": prepared_beneficiaries}]

    return CommentOptionsOperation(
        author=author_of_comment,
        permlink=permlink,
        max_accepted_payout=tt.Asset.Tbd(100),
        percent_hbd=10000,
        allow_votes=True,
        allow_curation_rewards=True,
        extensions=extensions,
    )


def prepare_operations_for_transactions(
    iterations: int, ops_in_one_element: int, elements_number_for_iteration
) -> list:
    """
    :param iterations: every iteration will multiply elements_number_for_iteration parameter
    :param ops_in_one_element: determines how many operations will be inserted in every element of output list
    :param elements_number_for_iteration will add chosen amount of records to output list
    :return: list filled with lists[operation1, operation2...]
    """
    output = []  # final list of lists that contains operations
    # list of lists containing permlinks of all comments, every first-dimensional list matches comments created during
    # every main iteration
    # block log contains 99999 prepared comments for first iteration
    comment_data = {f"permlink-{index}": f"account-{index}" for index in range(100_000)}  # comment permlinks with authors
    account_it = 0
    for main_iteration in range(iterations):
        comment_data_for_current_iteration = {}

        for y in range(elements_number_for_iteration):
            list_of_ops = []
            for _z in range(ops_in_one_element):
                if account_it >= 99_999:
                    account_it = 0
                generated_op = __prepare_operation(
                    f"account-{account_it}", comment_data, comment_data_for_current_iteration
                )
                list_of_ops.append(generated_op)
                # add comment options to new article
                if generated_op.get_name() == "comment" and generated_op.parent_author == "":
                    list_of_ops.append(create_comment_options(f"account-{account_it}", comment_data_for_current_iteration))
                account_it += 1
            output.append(list_of_ops)
        comment_data.update(comment_data_for_current_iteration)
    return output

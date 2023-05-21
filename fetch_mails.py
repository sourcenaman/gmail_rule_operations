if __name__ == "__main__":
    from helpers.database import create_db
    from helpers.get_emails import MailService
    from helpers.db_operations import InsertEmails

    #create sqlite database if doesn't exist already
    create_db()
    mail_service = MailService()

    #get all ids of all emails
    ids = mail_service.get_ids()

    #filter out latest 500 emails to avoid rate limiting while fetching emails
    ids = ids[:500]

    #raw emails
    mails = mail_service.get_mails(ids)

    #clean raw emails and insert in database
    InsertEmails(mails=mails)